from __future__ import annotations

TRANSLATIONS: dict[str, dict[str, str]] = {
    "app_title": {
        "ja": "StemScore - 楽譜生成AI",
        "en": "StemScore - AI Score Generator",
    },
    "subtitle": {
        "ja": "MP3から6パート楽譜を自動生成",
        "en": "MP3 → 6-Part Musical Score",
    },
    "upload_label": {
        "ja": "音声ファイルをアップロード",
        "en": "Upload audio file",
    },
    "suno_path_label": {
        "ja": "Sunoエクスポートフォルダのパス",
        "en": "Suno export directory path",
    },
    "genre_label": {
        "ja": "ジャンル",
        "en": "Genre",
    },
    "parts_label": {
        "ja": "抽出パート",
        "en": "Parts to extract",
    },
    "format_label": {
        "ja": "出力フォーマット",
        "en": "Output format",
    },
    "credit_mode_label": {
        "ja": "Sunoクレジットモード",
        "en": "Suno credit mode",
    },
    "transcribe_button": {
        "ja": "楽譜を生成する",
        "en": "Transcribe",
    },
    "processing": {
        "ja": "処理中...",
        "en": "Processing...",
    },
    "analysis_header": {
        "ja": "解析結果",
        "en": "Analysis Results",
    },
    "tempo_label": {
        "ja": "テンポ (BPM)",
        "en": "Tempo (BPM)",
    },
    "key_label": {
        "ja": "キー",
        "en": "Key",
    },
    "time_sig_label": {
        "ja": "拍子",
        "en": "Time Signature",
    },
    "output_header": {
        "ja": "出力ファイル",
        "en": "Output Files",
    },
    "download_button": {
        "ja": "ダウンロード",
        "en": "Download",
    },
    "error_message": {
        "ja": "エラーが発生しました",
        "en": "An error occurred",
    },
    "pipeline_info_title": {
        "ja": "パイプラインの説明",
        "en": "Pipeline explanation",
    },
    "step1": {
        "ja": "1. 解析: テンポ・キー・拍子を検出",
        "en": "1. Analyze: detect tempo, key, time signature",
    },
    "step2": {
        "ja": "2. 分離: Demucsでステム分離",
        "en": "2. Separate: split stems with Demucs",
    },
    "step3": {
        "ja": "3. 採譜: 各パートをMIDIに変換",
        "en": "3. Transcribe: convert each part to MIDI",
    },
    "step4": {
        "ja": "4. 組立: クォンタイズ・マージ・エクスポート",
        "en": "4. Assemble: quantize, merge, export",
    },
    "settings_label": {
        "ja": "設定",
        "en": "Settings",
    },
    "language_label": {
        "ja": "言語 / Language",
        "en": "Language",
    },
    "lead_vocal": {
        "ja": "リードボーカル",
        "en": "Lead Vocal",
    },
    "backing_vocal": {
        "ja": "バッキングボーカル",
        "en": "Backing Vocal",
    },
    "bass": {
        "ja": "ベース",
        "en": "Bass",
    },
    "drums": {
        "ja": "ドラム",
        "en": "Drums",
    },
    "backing_harmony": {
        "ja": "バッキングハーモニー",
        "en": "Backing Harmony",
    },
    "chords": {
        "ja": "コード",
        "en": "Chords",
    },
    "success_message": {
        "ja": "楽譜の生成が完了しました！",
        "en": "Score generation complete!",
    },
    "info_text": {
        "ja": "StemScoreは解析・分離・採譜・組立のパイプラインで楽譜を生成します。",
        "en": "StemScore runs analysis, separation, transcription, and assembly to generate scores.",
    },
    "pipeline_step_analysis": {
        "ja": "解析: テンポ・キー・拍子を検出",
        "en": "Analysis: detect tempo, key, time signature",
    },
    "pipeline_step_separation": {
        "ja": "分離: フルミックスをステム分離 (Route Bのみ)",
        "en": "Separation: split full mix into stems (Route B only)",
    },
    "pipeline_step_transcription": {
        "ja": "採譜: ステムをノートイベントへ変換",
        "en": "Transcription: convert stems into note events",
    },
    "pipeline_step_assembly": {
        "ja": "組立: クォンタイズしてMIDI/MusicXML/PDFに出力",
        "en": "Assembly: quantize and export MIDI/MusicXML/PDF",
    },
    "preview_header": {
        "ja": "楽譜プレビュー / Score Preview",
        "en": "Score Preview",
    },
    "preview_parts_label": {
        "ja": "プレビュー対象パート",
        "en": "Parts to preview",
    },
    "preview_tab_piano": {
        "ja": "ピアノロール / Piano Roll",
        "en": "Piano Roll",
    },
    "preview_tab_simple": {
        "ja": "簡易楽譜 / Simple Score",
        "en": "Simple Score",
    },
    "preview_tab_xml": {
        "ja": "MusicXML プレビュー",
        "en": "MusicXML Preview",
    },
    "preview_missing_xml": {
        "ja": "MusicXML出力が見つかりませんでした。",
        "en": "MusicXML output not found.",
    },
    "preview_error": {
        "ja": "プレビューの生成に失敗しました。",
        "en": "Failed to generate preview.",
    },
}


def t(key: str, lang: str) -> str:
    """Return translated UI string for the given key."""
    entry = TRANSLATIONS.get(key, {})
    return entry.get(lang, entry.get("en", key))
