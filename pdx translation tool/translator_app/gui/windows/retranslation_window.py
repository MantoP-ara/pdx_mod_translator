# translator_project/translator_app/gui/windows/retranslation_window.py
import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
import os
import threading
import codecs


class RetranslationWindow(ctk.CTkToplevel):
    """이미 번역된 파일에서 미번역된 부분을 찾아 재번역하는 도구"""
    
    def __init__(self, parent, main_app):
        super().__init__(parent)
        self.main_app = main_app
        self.title(main_app.texts.get("retranslation_window_title", "Retranslation Tool"))
        self.geometry("900x700")
        self.minsize(700, 500)
        
        self.untranslated_items = {}  # {file_path: [items]}
        self.check_vars = {}  # {(file, key): BooleanVar}
        self.stop_event = threading.Event()
        
        self._create_widgets()
        self.update_language()
    
    def _create_widgets(self):
        """UI 위젯 생성"""
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)
        
        # 상단 설명
        self.desc_label = ctk.CTkLabel(self, font=ctk.CTkFont(size=14, weight="bold"))
        self.desc_label.grid(row=0, column=0, padx=15, pady=(10, 5), sticky="w")
        
        # 버튼 프레임
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.grid(row=1, column=0, padx=10, pady=5, sticky="ew")
        
        self.scan_button = ctk.CTkButton(
            btn_frame,
            command=self._start_scan,
            width=180,
            height=32,
            fg_color="#1976D2",
            hover_color="#1565C0"
        )
        self.scan_button.pack(side="left", padx=(0, 5))
        
        self.select_all_button = ctk.CTkButton(
            btn_frame,
            command=self._select_all,
            width=100,
            height=32
        )
        self.select_all_button.pack(side="left", padx=5)
        
        self.deselect_all_button = ctk.CTkButton(
            btn_frame,
            command=self._deselect_all,
            width=100,
            height=32
        )
        self.deselect_all_button.pack(side="left", padx=5)
        
        self.retranslate_button = ctk.CTkButton(
            btn_frame,
            command=self._start_retranslation,
            width=180,
            height=32,
            fg_color="#2E7D32",
            hover_color="#388E3C",
            state="disabled"
        )
        self.retranslate_button.pack(side="right", padx=(5, 0))
        
        self.stop_button = ctk.CTkButton(
            btn_frame,
            command=self._stop_retranslation,
            width=80,
            height=32,
            fg_color="#D32F2F",
            hover_color="#E53935",
            state="disabled"
        )
        self.stop_button.pack(side="right", padx=5)
        
        # 결과 스크롤 프레임
        self.result_frame = ctk.CTkScrollableFrame(self)
        self.result_frame.grid(row=2, column=0, padx=10, pady=5, sticky="nsew")
        self.result_frame.grid_columnconfigure(0, weight=1)
        
        # 상태 표시줄
        status_frame = ctk.CTkFrame(self, fg_color="transparent", height=30)
        status_frame.grid(row=3, column=0, padx=10, pady=(5, 10), sticky="ew")
        
        self.status_label = ctk.CTkLabel(
            status_frame,
            font=ctk.CTkFont(size=12),
            text_color=("gray50", "gray60")
        )
        self.status_label.pack(side="left", padx=5)
        
        self.count_label = ctk.CTkLabel(
            status_frame,
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=("#1976D2", "#64B5F6")
        )
        self.count_label.pack(side="right", padx=5)
    
    def _start_scan(self):
        """미번역 항목 스캔 시작"""
        output_folder = self.main_app.output_folder_var.get()
        input_folder = self.main_app.input_folder_var.get()
        
        if not output_folder or not os.path.isdir(output_folder):
            texts = self.main_app.texts
            messagebox.showerror(
                texts.get("error_title", "Error"),
                texts.get("retranslation_no_output_folder", "Output folder not set")
            )
            return
        
        self.scan_button.configure(state="disabled")
        self._update_status(self.main_app.texts.get("retranslation_scanning", "Scanning files..."))
        
        # 결과 초기화
        for widget in self.result_frame.winfo_children():
            widget.destroy()
        self.untranslated_items.clear()
        self.check_vars.clear()
        
        thread = threading.Thread(
            target=self._scan_worker,
            args=(input_folder, output_folder),
            daemon=True
        )
        thread.start()
    
    def _scan_worker(self, input_folder, output_folder):
        """백그라운드에서 미번역 항목 스캔"""
        texts = self.main_app.texts
        source_lang = self.main_app.source_lang_for_api_var.get()
        target_lang = self.main_app.target_lang_for_api_var.get()
        engine = self.main_app.translator_engine
        
        # 출력 폴더에서 번역된 파일 찾기
        translated_files = []
        for root, _, files in os.walk(output_folder):
            for f in files:
                if f.lower().endswith(('.yml', '.yaml')):
                    translated_files.append(os.path.join(root, f))
        
        self.after(0, lambda: self._update_status(
            texts.get("retranslation_found_files", "Found {0} translated files").format(len(translated_files))
        ))
        
        total_untranslated = 0
        
        for translated_file in translated_files:
            # 대응하는 원본 파일 찾기
            original_file = self._find_original_file(translated_file, input_folder, output_folder, source_lang, target_lang)
            
            if not original_file or not os.path.exists(original_file):
                continue
            
            items = engine.scan_untranslated_in_file(
                original_file, translated_file, source_lang, target_lang
            )
            
            if items:
                self.untranslated_items[translated_file] = {
                    "original_file": original_file,
                    "items": items
                }
                total_untranslated += len(items)
        
        # UI 업데이트 (메인 스레드)
        self.after(0, lambda: self._display_scan_results(total_untranslated))
    
    def _find_original_file(self, translated_file, input_folder, output_folder, source_lang, target_lang):
        """번역된 파일에 대응하는 원본 파일 찾기"""
        from ...utils.localization import get_language_code
        
        source_code = get_language_code(source_lang).lower()
        target_code = get_language_code(target_lang).lower()
        
        # 출력 폴더 기준으로 상대 경로 계산
        rel_path = os.path.relpath(translated_file, output_folder)
        
        # 파일명에서 대상 언어 코드를 원본 언어 코드로 변환
        dir_part = os.path.dirname(rel_path)
        file_name = os.path.basename(rel_path)
        
        original_name = file_name.replace(f"l_{target_code}", f"l_{source_code}")
        
        original_path = os.path.join(input_folder, dir_part, original_name)
        
        if os.path.exists(original_path):
            return original_path
        
        # 대소문자 무시하고 검색
        import re
        pattern = re.compile(re.escape(f"l_{target_code}"), re.IGNORECASE)
        original_name_ci = pattern.sub(f"l_{source_code}", file_name)
        original_path_ci = os.path.join(input_folder, dir_part, original_name_ci)
        
        if os.path.exists(original_path_ci):
            return original_path_ci
        
        return None
    
    def _display_scan_results(self, total_untranslated):
        """스캔 결과 표시"""
        texts = self.main_app.texts
        
        for widget in self.result_frame.winfo_children():
            widget.destroy()
        self.check_vars.clear()
        
        if total_untranslated == 0:
            label = ctk.CTkLabel(
                self.result_frame,
                text=texts.get("retranslation_no_untranslated", "No untranslated items found"),
                font=ctk.CTkFont(size=13)
            )
            label.pack(pady=20)
            self.retranslate_button.configure(state="disabled")
        else:
            row_idx = 0
            for file_path, file_data in self.untranslated_items.items():
                items = file_data["items"]
                
                # 파일 헤더
                file_header = ctk.CTkLabel(
                    self.result_frame,
                    text=f"📄 {os.path.basename(file_path)} ({len(items)} items)",
                    font=ctk.CTkFont(size=13, weight="bold"),
                    anchor="w"
                )
                file_header.grid(row=row_idx, column=0, padx=5, pady=(10, 5), sticky="w")
                row_idx += 1
                
                for item in items:
                    item_frame = ctk.CTkFrame(self.result_frame)
                    item_frame.grid(row=row_idx, column=0, padx=10, pady=2, sticky="ew")
                    item_frame.grid_columnconfigure(1, weight=1)
                    
                    var = tk.BooleanVar(value=True)
                    self.check_vars[(file_path, item["key"])] = var
                    
                    cb = ctk.CTkCheckBox(item_frame, text="", variable=var, width=24)
                    cb.grid(row=0, column=0, padx=(5, 2), pady=3)
                    
                    # 키 표시
                    key_label = ctk.CTkLabel(
                        item_frame,
                        text=item["key"],
                        font=ctk.CTkFont(size=11, weight="bold"),
                        anchor="w"
                    )
                    key_label.grid(row=0, column=1, padx=5, pady=3, sticky="w")
                    
                    # 이유 표시
                    reason_text = texts.get(f"retranslation_reason_{item['reason']}", item['reason'])
                    reason_label = ctk.CTkLabel(
                        item_frame,
                        text=f"[{reason_text}]",
                        font=ctk.CTkFont(size=10),
                        text_color=("#D32F2F", "#E57373")
                    )
                    reason_label.grid(row=0, column=2, padx=5, pady=3, sticky="e")
                    
                    # 원본/현재 값 표시
                    original_preview = item["original"][:80] + "..." if len(item["original"]) > 80 else item["original"]
                    current_preview = item["current"][:80] + "..." if len(item["current"]) > 80 else item["current"]
                    
                    detail_label = ctk.CTkLabel(
                        item_frame,
                        text=f"{texts.get('retranslation_original', 'Original')}: {original_preview}\n{texts.get('retranslation_current', 'Current')}: {current_preview}",
                        font=ctk.CTkFont(size=10),
                        anchor="w",
                        justify="left",
                        wraplength=700
                    )
                    detail_label.grid(row=1, column=0, columnspan=3, padx=(30, 5), pady=(0, 3), sticky="w")
                    
                    row_idx += 1
            
            self.retranslate_button.configure(state="normal")
        
        self._update_status(
            texts.get("retranslation_scan_complete", "Scan Complete")
        )
        self._update_count()
        self.scan_button.configure(state="normal")
    
    def _select_all(self):
        """모든 항목 선택"""
        for var in self.check_vars.values():
            var.set(True)
        self._update_count()
    
    def _deselect_all(self):
        """모든 항목 선택 해제"""
        for var in self.check_vars.values():
            var.set(False)
        self._update_count()
    
    def _update_count(self):
        """선택된 항목 수 업데이트"""
        selected = sum(1 for var in self.check_vars.values() if var.get())
        texts = self.main_app.texts
        self.count_label.configure(
            text=f"{selected} {texts.get('retranslation_items_selected', 'items selected')}"
        )
    
    def _update_status(self, text):
        """상태 표시 업데이트"""
        self.status_label.configure(text=text)
    
    def _start_retranslation(self):
        """선택된 항목 재번역 시작"""
        texts = self.main_app.texts
        
        # API 키 확인
        api_key = self.main_app.api_key_var.get().strip()
        model_name = self.main_app.model_name_var.get()
        if not api_key or not model_name:
            messagebox.showerror(
                texts.get("error_title", "Error"),
                texts.get("retranslation_api_error", "API key and model must be configured")
            )
            return
        
        # 선택된 항목 수집
        selected_items = {}
        for (file_path, key), var in self.check_vars.items():
            if var.get():
                if file_path not in selected_items:
                    selected_items[file_path] = []
                # 해당 파일의 items에서 key로 찾기
                file_data = self.untranslated_items.get(file_path, {})
                for item in file_data.get("items", []):
                    if item["key"] == key:
                        selected_items[file_path].append(item)
                        break
        
        if not selected_items:
            return
        
        self.retranslate_button.configure(state="disabled")
        self.stop_button.configure(state="normal")
        self.stop_event.clear()
        self._update_status(texts.get("retranslation_in_progress", "Retranslating..."))
        
        thread = threading.Thread(
            target=self._retranslation_worker,
            args=(selected_items,),
            daemon=True
        )
        thread.start()
    
    def _retranslation_worker(self, selected_items):
        """백그라운드에서 재번역 수행"""
        engine = self.main_app.translator_engine
        texts = self.main_app.texts
        
        # 엔진 설정
        engine.api_key = self.main_app.api_key_var.get().strip()
        engine.selected_model_name = self.main_app.model_name_var.get()
        engine.source_lang_for_api = self.main_app.source_lang_for_api_var.get()
        engine.target_lang_for_api = self.main_app.target_lang_for_api_var.get()
        engine.prompt_template_str = self.main_app.prompt_glossary_panel.get_prompt_text() if hasattr(self.main_app, 'prompt_glossary_panel') else self.main_app.default_prompt_template_str
        engine.prefill_text = self.main_app.prompt_glossary_panel.get_prefill_text() if hasattr(self.main_app, 'prompt_glossary_panel') else ""
        engine.system_instruction = self.main_app.prompt_glossary_panel.get_system_instruction_text() if hasattr(self.main_app, 'prompt_glossary_panel') else ""
        engine.model_role_text = self.main_app.prompt_glossary_panel.get_model_role_text() if hasattr(self.main_app, 'prompt_glossary_panel') else ""
        engine.glossary_str_for_prompt = self.main_app._get_combined_glossary_content()
        engine.batch_size = self.main_app.batch_size_var.get()
        engine.max_tokens = self.main_app.max_tokens_var.get()
        engine.temperature = self.main_app.temperature_var.get()
        engine.delay_between_batches = self.main_app.delay_between_batches_var.get()
        engine.stop_event = self.stop_event
        
        total_retranslated = 0
        
        for file_path, items in selected_items.items():
            if self.stop_event.is_set():
                break
            
            count = engine.retranslate_items(file_path, items)
            total_retranslated += count
        
        # UI 업데이트
        self.after(0, lambda: self._retranslation_complete(total_retranslated))
    
    def _retranslation_complete(self, count):
        """재번역 완료 후 UI 업데이트"""
        texts = self.main_app.texts
        self.retranslate_button.configure(state="normal")
        self.stop_button.configure(state="disabled")
        
        self._update_status(
            texts.get("retranslation_complete", "Retranslation completed") + f" ({count})"
        )
        
        if count > 0:
            result = messagebox.askyesno(
                texts.get("info_title", "Information"),
                texts.get("retranslation_rescan_prompt", "Retranslation completed. Would you like to scan again?")
            )
            if result:
                self._start_scan()
    
    def _stop_retranslation(self):
        """재번역 중지"""
        self.stop_event.set()
        texts = self.main_app.texts
        self._update_status(texts.get("retranslation_stopping", "Stopping..."))
    
    def update_language(self):
        """UI 언어 업데이트"""
        texts = self.main_app.texts
        self.title(texts.get("retranslation_window_title", "Retranslation Tool"))
        self.desc_label.configure(text=texts.get("retranslation_window_description", "Detect and retranslate untranslated text segments"))
        self.scan_button.configure(text=texts.get("retranslation_scan_button", "Scan for Untranslated Text"))
        self.select_all_button.configure(text=texts.get("retranslation_select_all", "Select All"))
        self.deselect_all_button.configure(text=texts.get("retranslation_deselect_all", "Deselect All"))
        self.retranslate_button.configure(text=texts.get("retranslation_retranslate_button", "Retranslate Selected"))
        self.stop_button.configure(text=texts.get("stop_button", "Stop"))
        self.status_label.configure(text=texts.get("retranslation_status_ready", "Ready to scan"))
        self.count_label.configure(text="")
