import os
import pandas as pd
from pathlib import Path
from typing import List, Tuple
from .schema import DefectInfo, RepairdInfo
import re
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime


class FileManager:
    """ファイル操作を管理するクラス"""

    @staticmethod
    def create_repaird_csv_path(data_directory: str, current_lot_number: str) -> str:
        """
        指図に対応する修理データCSVファイル名を生成
        ### Args:
            data_directory (str): データディレクトリ
            current_lot_number (str): 現在の指図
        ### Raises:
            ValueError: current_lot_numberまたはdata_directoryが設定されていない場合
        ### Returns:
            str: 修理データCSVファイルのパス
        """

        # current_lot_numberが設定されているか確認
        if not current_lot_number:
            raise ValueError("Current lot number is not set.")
        # データディレクトリが設定されているか確認
        if not data_directory:
            raise ValueError("Not Setting Data Directory")
        # ファイル名を生成
        filename = f"{current_lot_number}_repaird_list.csv"
        # フルパスを返す
        return os.path.join(data_directory, filename)

    @staticmethod
    def create_defect_csv_path(
        data_directory: str, lot_number: str, image_filename: str
    ) -> str:
        """
        不良データCSVファイルのパスを生成
        ### Args:
            data_directory (str): データディレクトリ
            lot_number (str): 指図
            image_filename (str): 画像ファイル名（拡張子なし）
        ### Raises:
            ValueError: lot_number, image_filename, data_directoryが設定されていない場合
        ### Returns:
            str: 不良データCSVファイルのパス
        """
        # 指図が設定されているか確認
        if not lot_number:
            raise ValueError("Lot number is not set.")
        # 画像ファイル名が設定されているか確認
        if not image_filename:
            raise ValueError("Image filename is not set.")
        # データディレクトリが設定されているか確認
        if not data_directory:
            raise ValueError("Data directory is not set.")

        # ファイル名を生成
        filename = f"{lot_number}_{image_filename}.csv"
        # フルパスを返す
        return os.path.join(data_directory, filename)

    @staticmethod
    def read_defect_csv(filepath: str) -> List[DefectInfo]:
        """
        CSVファイルから不良リストを読み込み
        ### Args:
            filepath (str): CSVファイルのパス
        ### Raises:
            Exception: ファイル読み込みエラー
        ### Returns:
            List[DefectInfo]: 不良情報リスト
        """
        try:
            # ファイルの存在を確認
            if not Path(filepath).exists():
                return []
            # CSVを読み込み
            df = pd.read_csv(filepath, encoding="utf-8-sig")
            # NaNを空文字列に置換
            df = df.fillna("")
            # DefectInfoのリストに変換して返す
            return [DefectInfo(**row) for row in df.to_dict(orient="records")]
        except Exception as e:
            raise Exception(f"Failed to read defect CSV: {e}")

    @staticmethod
    def read_repaird_csv(filepath: str) -> List[RepairdInfo]:
        """
        CSVファイルから修理データを読み込み
        ### Args:
            filepath (str): CSVファイルのパス
        ### Raises:
            Exception: ファイル読み込みエラー
        ### Returns:
            List[RepairdInfo]: 修理済み情報リスト
        """
        try:
            # ファイルの存在を確認
            if not Path(filepath).exists():
                return []
            # CSVを読み込み
            df = pd.read_csv(filepath, encoding="utf-8-sig")
            # NaNを適切な値に置換
            df = df.fillna(
                {
                    "is_repaird": False,
                    "parts_type": "",
                    "insert_datetime": "",
                    "kintone_record_id": "",
                }
            )
            # RepairdInfoのリストに変換して返す
            return [RepairdInfo(**row) for row in df.to_dict(orient="records")]
        except Exception as e:
            raise Exception(f"Failed to read repaird CSV: {e}")

    @staticmethod
    def save_defect_csv(defect_list: List[DefectInfo], filepath: str) -> None:
        """
        不良リストをCSVファイルに保存
        ### Args:
            defect_list (List[DefectInfo]): 不良情報リスト
            filepath (str): 保存先CSVファイルのパス
        ### Raises:
            PermissionError: ファイルが他のプロセスで使用中の場合
            OSError: その他のOSエラー
            Exception: ファイル保存エラー
        """
        try:
            # DataFrameに変換して保存
            df = pd.DataFrame([defect.__dict__ for defect in defect_list])
            # インデックスを振らずにCSVに保存
            df.to_csv(filepath, index=False, encoding="utf-8-sig")
        except PermissionError as e:
            raise PermissionError(f"Permission denied when saving defect CSV: {e}")
        except OSError as e:
            raise OSError(f"OS error when saving defect CSV: {e}")
        except Exception as e:
            raise Exception(f"Failed to save defect CSV: {e}")

    @staticmethod
    def save_repaird_csv(repaird_list: List[RepairdInfo], filepath: str) -> None:
        """
        修理データをCSVファイルに保存
        ### Args:
            repaird_list (List[RepairdInfo]): 修理済み情報リスト
            filepath (str): 保存先CSVファイルのパス
        ### Raises:
            Exception: ファイル保存エラー
        """
        try:
            # DataFrameに変換して保存
            df = pd.DataFrame([repaird.__dict__ for repaird in repaird_list])
            # インデックスを振らずにCSVに保存
            df.to_csv(filepath, index=False, encoding="utf-8-sig")
        except Exception as e:
            raise Exception(f"Failed to save repaird CSV: {e}")

    @staticmethod
    def read_defect_mapping(mapping_path: str) -> pd.DataFrame:
        """
        不良名マッピングファイルを読み込み
        ### Args:
            mapping_path (str): 不良名マッピングCSVファイルのパス
        ### Raises:
            FileNotFoundError: defect_mapping.csvが存在しない場合
        ### Returns:
            pd.DataFrame: 不良名マッピングデータフレーム
        """
        # ファイルの存在を確認
        if not Path(mapping_path).exists():
            raise FileNotFoundError(f"defect_mapping.csv not found at {mapping_path}")
        # CSVを読み込み、欠損値を削除して返す
        df = pd.read_csv(mapping_path, encoding="utf-8-sig")
        # 不良名マッピングの列を指定
        return df.dropna()

    @staticmethod
    def read_user_csv(user_csv_path: str) -> pd.DataFrame:
        """
        ユーザーCSVファイルを読み込み
        ### Args:
            user_csv_path (str): ユーザーCSVファイルのパス
        ### Raises:
            FileNotFoundError: user.csvが存在しない場合
        ### Returns:
            pd.DataFrame: ユーザーデータフレーム
        """
        # ファイルの存在を確認
        if not Path(user_csv_path).exists():
            raise FileNotFoundError(f"user.csv not found at {user_csv_path}")
        # CSVを読み込みして返す
        return pd.read_csv(user_csv_path, encoding="utf-8-sig")

    @staticmethod
    def create_kintone_settings_file(
        settings_path: str, subdomain: str, app_id: str, api_token: str
    ) -> bool:
        """
        kintone設定ファイルを作成
        ### Args:
            settings_path (str): kintone_settings.jsonのパス
            subdomain (str): kintoneのサブドメイン
            app_id (str): kintoneアプリID
            api_token (str): kintone APIトークン
        ### Returns:
            bool: ファイル作成に成功したかどうか
        """
        try:
            import json

            settings = {
                "subdomain": subdomain,
                "app_id": app_id,
                "api_token": api_token,
            }
            with open(settings_path, "w", encoding="utf-8-sig") as f:
                json.dump(settings, f, ensure_ascii=False, indent=4)
            return True
        except Exception as e:
            print(f"Failed to create kintone settings file: {e}")
            return False

    @staticmethod
    def load_kintone_settings_file(settings_path: str) -> dict:
        """
        kintone設定ファイルを読み込み
        ### Args:
            settings_path (str): kintone_settings.jsonのパス
        ### Raises:
            FileNotFoundError: kintone_settings.jsonが存在しない場合
            Exception: ファイル読み込みエラー
        ### Returns:
            dict: kintone設定辞書
        """
        try:
            import json

            # ファイルの存在を確認
            if not Path(settings_path).exists():
                raise FileNotFoundError(
                    f"kintone_settings.json not found at {settings_path}"
                )
            with open(settings_path, "r", encoding="utf-8-sig") as f:
                settings = json.load(f)
            return settings
        except FileNotFoundError as fnf_error:
            raise fnf_error
        except Exception as e:
            raise Exception(f"Failed to load kintone settings file: {e}")

    @staticmethod
    def get_image_path(image_directory: str, lot_number: str, item_code: str) -> str:
        """
        指図に対応する画像ディレクトリのパスを生成
        ### Args:
            data_directory (str): データディレクトリ
            lot_number (str): 指図
            item_code (str): 品目コード
        ### Raises:
            ValueError: lot_numberの形式が不正な場合
            FileNotFoundError: 画像ファイルが存在しない場合
        ### Returns:
            str: 画像ディレクトリのパス
        """
        # lotnumberの形式が正しいか確認
        if not re.match(r"^[0-9]{7}-[0-9]{2}", lot_number):
            raise ValueError("Invalid lot number format.")

        # lotnumberの末尾の2桁を取得
        lot_suffix = lot_number[-2:]

        # ファイル名の正規表現パターン
        pattern = rf"^{re.escape(item_code)}_{lot_suffix}_.*$"

        # image_directory以下のディレクトリを走査
        image_path = Path(image_directory)
        for dir_entry in image_path.iterdir():
            if re.match(pattern, dir_entry.name):
                return str(dir_entry.name)
        raise FileNotFoundError("Image directory not found.")

    @staticmethod
    def parse_image_filename(image_filename: str) -> Tuple[str, str, str]:
        """
        画像ファイル名から品目コードと指図を抽出
        ### Args:
            image_filename (str): 画像ファイル名（拡張子あり/なし両対応）
        ### Raises:
            ValueError: 画像ファイル名の形式が不正な場合
        ### Returns:
            (str, str, str): モデル名、基板名、基板面のタプル
        """

        # 拡張子を除去
        filename_without_ext = image_filename
        if "." in image_filename:
            filename_without_ext = image_filename.rsplit(".", 1)[0]

        # 修正された正規表現パターン（5フィールド）
        # パターン: 品目コード_2桁数字_モデル名_基板名_基板面
        match = re.match(r"^.*_[0-9]{2}_.*_.*_.*$", filename_without_ext)
        if not match:
            raise ValueError(f"Invalid image filename format: {image_filename}")

        # アンダースコアで分割
        parts = filename_without_ext.split("_")

        # 最低5つのパートが必要
        if len(parts) < 5:
            raise ValueError(
                f"Invalid filename format. Expected at least 5 parts: {image_filename}"
            )

        # 2番目のパートが2桁の数字であることを再確認
        if not re.match(r"^\d{2}$", parts[1]):
            raise ValueError(f"Second part should be 2-digit number: {parts[1]}")

        model_name = parts[2]
        board_name = parts[3]
        board_side = parts[4]

        return model_name, board_name, board_side

    @staticmethod
    def export_canvas_image_with_markers(
        defect: DefectInfo,
        image_path: str,
        output_dir: str,
        filename: str = None,
        marker_size: int = 10,
        marker_color: str = "red",
        image_format: str = "PNG",
        quality: int = 95,
        font_size: int = None,
    ):
        """
        Canvas内の画像に座標マーカーを描画した状態で画像を生成し、指定したディレクトリに保存する

        Args:
            output_dir (str): 出力先ディレクトリのパス
            reference (str): リファレンス情報（画像下部に表示）。Noneの場合は表示しない
            defect_name (str): 不良名（画像下部に表示）。Noneの場合は表示しない
            filename (str): 出力ファイル名（拡張子なし）。Noneの場合は"元ファイル名_marked_タイムスタンプ"を使用
            marker_size (int): マーカーのサイズ（直径、ピクセル単位）デフォルト10
            marker_color (str): マーカーの色（PIL形式: "red", "#FF0000"など）デフォルト"red"
            image_format (str): 画像フォーマット（"PNG", "JPEG", "BMP"など）デフォルト"PNG"
            quality (int): 画像品質（1-100、JPEGの場合は品質、PNGの場合は圧縮レベル0-9に変換）デフォルト95
            font_size (int): テキストのフォントサイズ（ピクセル単位）。Noneの場合は画像サイズから自動計算

        Returns:
            str: 保存した画像のパス（保存に失敗した場合はNone）
        """

        # 出力ディレクトリの作成
        output_path = Path(output_dir)
        if not output_path.exists():
            try:
                output_path.mkdir(parents=True, exist_ok=True)
            except Exception as e:
                error_msg = f"出力ディレクトリの作成に失敗しました: {e}"
                raise ValueError(error_msg)

        try:
            # 元の画像を開く
            original_image = Image.open(image_path)
            original_width, original_height = original_image.size

            # 描画オブジェクトを作成
            draw = ImageDraw.Draw(original_image)

            # 各不良のマーカーを描画
            marker_radius = marker_size // 2
            # 相対座標を実際のピクセル座標に変換
            pixel_x = defect.x * original_width
            pixel_y = defect.y * original_height

            # 楕円（マーカー）の境界ボックスを計算
            left = pixel_x - marker_radius
            top = pixel_y - marker_radius
            right = pixel_x + marker_radius
            bottom = pixel_y + marker_radius

            # マーカーを描画（外枠と塗りつぶし）
            draw.ellipse(
                [left, top, right, bottom], outline=marker_color, width=2, fill=None
            )

            # referenceとdefect_nameの描画（指定されている場合）
            reference = defect.reference
            defect_name = defect.defect_name
            if reference or defect_name:
                # フォントサイズの決定（引数が指定されていれば使用、なければ自動計算）
                if font_size is None:
                    # 画像サイズに応じて自動調整（最小30、最大80）
                    calculated_font_size = max(30, min(80, original_height // 20))
                else:
                    # 引数で指定されたフォントサイズを使用（範囲制限: 10-200）
                    calculated_font_size = max(10, min(200, font_size))

                try:
                    # システムフォントを試行（日本語対応）
                    font = None
                    # Windows/macOS/Linuxの日本語フォント候補
                    font_candidates = [
                        # Windows日本語フォント
                        "C:/Windows/Fonts/msgothic.ttc",  # MSゴシック
                        "C:/Windows/Fonts/meiryo.ttc",  # メイリオ
                        "C:/Windows/Fonts/YuGothM.ttc",  # 游ゴシック Medium
                        "C:/Windows/Fonts/YuGothR.ttc",  # 游ゴシック Regular
                        "C:/Windows/Fonts/msmincho.ttc",  # MS明朝
                        # macOS日本語フォント
                        "/System/Library/Fonts/ヒラギノ角ゴシック W3.ttc",
                        "/System/Library/Fonts/Hiragino Sans GB.ttc",
                        # Linux日本語フォント
                        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
                        "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
                    ]
                    for font_path in font_candidates:
                        if os.path.exists(font_path):
                            try:
                                font = ImageFont.truetype(
                                    font_path, calculated_font_size
                                )
                                break
                            except Exception as e:
                                print(f"フォント読み込みエラー ({font_path}): {e}")
                                continue

                    # フォントが見つからない場合は警告
                    if font is None:
                        print(
                            "警告: 日本語フォントが見つかりませんでした。デフォルトフォントを使用します。"
                        )
                        # Pillow 10.0.0以降ではload_default()にsizeパラメータが使用可能
                        try:
                            font = ImageFont.load_default(size=calculated_font_size)
                        except TypeError:
                            # 古いバージョンのPillowの場合
                            font = ImageFont.load_default()
                except Exception as e:
                    # フォント読み込み失敗時はデフォルトフォント
                    print(f"フォント初期化エラー: {e}")
                    try:
                        font = ImageFont.load_default(size=calculated_font_size)
                    except TypeError:
                        font = ImageFont.load_default()

                # テキストの構築
                text_lines = []
                if reference:
                    text_lines.append(f"リファレンス: {reference}")
                if defect_name:
                    text_lines.append(f"不良名: {defect_name}")

                # 各行の描画位置を計算
                line_height = font_size + 10
                total_text_height = len(text_lines) * line_height + 2  # 上下マージン

                # テキスト背景の矩形を描画（半透明の黒背景）
                text_bg_top = original_height - total_text_height
                draw.rectangle(
                    [0, text_bg_top, original_width, original_height],
                    fill=(0, 0, 0, 20),
                )

                # テキストを描画
                y_position = text_bg_top + 10
                for text_line in text_lines:
                    draw.text((10, y_position), text_line, fill="white", font=font)
                    y_position += line_height

            # 出力ファイル名を生成
            file_extension = image_format.lower()
            if filename:
                # ユーザー指定のファイル名を使用（拡張子は除去）
                base_filename = Path(filename).stem
                output_filename = f"{base_filename}.{file_extension}"
            else:
                # デフォルト: 元ファイル名 + タイムスタンプ
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                original_filename = Path(image_path).stem
                output_filename = (
                    f"{original_filename}_marked_{timestamp}.{file_extension}"
                )

            output_filepath = output_path / output_filename

            # 画像形式に応じた保存オプションを設定
            save_kwargs = {}
            if image_format.upper() == "JPEG" or image_format.upper() == "JPG":
                # JPEG: 品質を1-100で指定
                save_kwargs["quality"] = max(1, min(100, quality))
                save_kwargs["optimize"] = True
                # JPEGはRGBモードが必要
                if original_image.mode in ("RGBA", "LA", "P"):
                    # 透明度がある場合は白背景に合成
                    background = Image.new("RGB", original_image.size, (255, 255, 255))
                    if original_image.mode == "P":
                        original_image = original_image.convert("RGBA")
                    background.paste(
                        original_image,
                        mask=(
                            original_image.split()[-1]
                            if original_image.mode in ("RGBA", "LA")
                            else None
                        ),
                    )
                    original_image = background
                elif original_image.mode != "RGB":
                    original_image = original_image.convert("RGB")
            elif image_format.upper() == "PNG":
                # PNG: 圧縮レベルを0-9で指定（qualityを100段階から9段階に変換）
                compress_level = max(0, min(9, int((100 - quality) / 11)))
                save_kwargs["compress_level"] = compress_level
                save_kwargs["optimize"] = True
            elif image_format.upper() == "BMP":
                # BMP: 特別なオプションなし
                pass
            else:
                # その他のフォーマット: 基本設定
                if image_format.upper() in ("TIFF", "TIF"):
                    save_kwargs["compression"] = "tiff_lzw"

            # 画像を保存
            original_image.save(
                output_filepath, format=image_format.upper(), **save_kwargs
            )

            return str(output_filepath)

        except Exception as e:
            error_msg = f"画像のエクスポートに失敗しました: {e}"
            raise ValueError(error_msg)

    @staticmethod
    def delete_exported_image(
        output_dir: str, filename: str, image_format: str = "PNG"
    ):
        """
        export_canvas_image_with_markersで生成された画像ファイルを削除する

        Args:
            output_dir (str): 画像が保存されているディレクトリのパス
            filename (str): 削除する画像のファイル名（拡張子なし）
            image_format (str): 画像フォーマット（"PNG", "JPEG", "BMP"など）デフォルト"PNG"

        Returns:
            bool: 削除に成功した場合True、失敗した場合False
        """
        try:
            # ファイルパスを構築
            file_extension = image_format.lower()
            output_path = Path(output_dir)

            # ファイル名から拡張子を除去
            base_filename = Path(filename).stem
            target_filename = f"{base_filename}.{file_extension}"
            target_filepath = output_path / target_filename

            # ファイルが存在するか確認
            if not target_filepath.exists():
                warning_msg = f"削除対象のファイルが見つかりません: {target_filepath}"
                raise ValueError(warning_msg)

            # ファイルを削除
            target_filepath.unlink()

            success_msg = f"画像ファイルを削除しました: {target_filepath}"
            return success_msg

        except PermissionError as e:
            error_msg = f"ファイル削除の権限がありません: {e}"
            raise ValueError(error_msg)
        except Exception as e:
            error_msg = f"画像ファイルの削除に失敗しました: {e}"
            raise (error_msg)
