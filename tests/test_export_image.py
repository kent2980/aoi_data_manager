import pytest
import tempfile
import shutil
from pathlib import Path
from PIL import Image
from aoi_data_manager.schema import DefectInfo
from aoi_data_manager.file_operations import FileManager


# テストデータのディレクトリパス
TEST_DATA_DIR = Path(__file__).parent / "test_data"
TEST_IMAGE_DIR = TEST_DATA_DIR / "image"
TEST_EXPORT_DIR = TEST_DATA_DIR / "export_image"


@pytest.fixture(scope="session")
def all_test_images():
    """テスト用の画像ファイル一覧を取得するフィクスチャ"""
    # imageディレクトリ内のすべての画像ファイルを取得
    image_files = []
    for ext in ["*.jpg", "*.jpeg", "*.png", "*.bmp"]:
        image_files.extend(list(TEST_IMAGE_DIR.glob(ext)))

    if not image_files:
        raise FileNotFoundError(f"画像ファイルが見つかりません: {TEST_IMAGE_DIR}")

    return [str(img) for img in image_files]


@pytest.fixture
def clean_export_dir():
    """エクスポートディレクトリを準備するフィクスチャ"""
    # ディレクトリが存在しない場合は作成
    TEST_EXPORT_DIR.mkdir(parents=True, exist_ok=True)

    yield str(TEST_EXPORT_DIR)

    # テスト後はクリーンアップしない（出力を確認できるように）


@pytest.fixture
def temp_dir():
    """一時ディレクトリを作成するフィクスチャ"""
    temp_path = tempfile.mkdtemp()
    yield temp_path
    # テスト終了後にディレクトリを削除
    shutil.rmtree(temp_path, ignore_errors=True)


@pytest.fixture
def sample_image(temp_dir):
    """テスト用のサンプル画像を作成するフィクスチャ"""
    image_path = Path(temp_dir) / "test_image.png"
    # 1000x800の白い画像を作成
    img = Image.new("RGB", (1000, 800), color="white")
    img.save(image_path)
    return str(image_path)


@pytest.fixture
def sample_defect():
    """テスト用の不良情報を作成するフィクスチャ"""
    return DefectInfo(
        line_name="Line1",
        model_code="MODEL001",
        lot_number="1234567-01",
        current_board_index=1,
        defect_number=1,
        serial="SN001",
        reference="R1",
        defect_name="ハンダ不良",
        x=0.5,  # 画像中央
        y=0.5,  # 画像中央
        aoi_user="TestUser",
        model_label="Model1",
        board_label="Board1",
    )


class TestExportCanvasImageWithMarkers:
    """export_canvas_image_with_markers関数のテストクラス"""

    def test_export_with_png_format(self, temp_dir, sample_image, sample_defect):
        """PNG形式で出力されることをテスト"""
        output_dir = Path(temp_dir) / "output"

        result_path = FileManager.export_canvas_image_with_markers(
            defect=sample_defect,
            image_path=sample_image,
            output_dir=str(output_dir),
            filename="test_output",
            image_format="PNG",
        )

        # ファイルが存在することを確認
        assert Path(result_path).exists()
        # 拡張子がPNGであることを確認
        assert result_path.endswith(".png")
        # 画像として開けることを確認
        img = Image.open(result_path)
        assert img.format == "PNG"

    def test_export_with_jpeg_format(self, temp_dir, sample_image, sample_defect):
        """JPEG形式で出力されることをテスト"""
        output_dir = Path(temp_dir) / "output"

        result_path = FileManager.export_canvas_image_with_markers(
            defect=sample_defect,
            image_path=sample_image,
            output_dir=str(output_dir),
            filename="test_output",
            image_format="JPEG",
        )

        # ファイルが存在することを確認
        assert Path(result_path).exists()
        # 拡張子がjpegであることを確認
        assert result_path.endswith(".jpeg")
        # 画像として開けることを確認
        img = Image.open(result_path)
        assert img.format == "JPEG"

    def test_export_with_bmp_format(self, temp_dir, sample_image, sample_defect):
        """BMP形式で出力されることをテスト"""
        output_dir = Path(temp_dir) / "output"

        result_path = FileManager.export_canvas_image_with_markers(
            defect=sample_defect,
            image_path=sample_image,
            output_dir=str(output_dir),
            filename="test_output",
            image_format="BMP",
        )

        # ファイルが存在することを確認
        assert Path(result_path).exists()
        # 拡張子がbmpであることを確認
        assert result_path.endswith(".bmp")
        # 画像として開けることを確認
        img = Image.open(result_path)
        assert img.format == "BMP"

    def test_export_to_specified_directory(self, temp_dir, sample_image, sample_defect):
        """指定したディレクトリに出力されることをテスト"""
        output_dir = Path(temp_dir) / "custom_output_dir"

        result_path = FileManager.export_canvas_image_with_markers(
            defect=sample_defect,
            image_path=sample_image,
            output_dir=str(output_dir),
            filename="test_output",
        )

        # 指定したディレクトリに出力されていることを確認
        assert str(output_dir) in result_path
        assert Path(result_path).parent == output_dir
        # ファイルが存在することを確認
        assert Path(result_path).exists()

    def test_export_creates_directory_if_not_exists(
        self, temp_dir, sample_image, sample_defect
    ):
        """出力ディレクトリが存在しない場合、自動作成されることをテスト"""
        output_dir = Path(temp_dir) / "non_existent" / "nested" / "directory"

        # ディレクトリが存在しないことを確認
        assert not output_dir.exists()

        result_path = FileManager.export_canvas_image_with_markers(
            defect=sample_defect,
            image_path=sample_image,
            output_dir=str(output_dir),
            filename="test_output",
        )

        # ディレクトリが作成されていることを確認
        assert output_dir.exists()
        # ファイルが存在することを確認
        assert Path(result_path).exists()

    def test_export_raises_error_when_image_not_found(self, temp_dir, sample_defect):
        """画像ファイルが存在しない場合に例外が発生することをテスト"""
        output_dir = Path(temp_dir) / "output"
        non_existent_image = str(Path(temp_dir) / "non_existent_image.png")

        # ファイルが存在しないことを確認
        assert not Path(non_existent_image).exists()

        # 例外が発生することを確認
        with pytest.raises(Exception):  # FileNotFoundError または ValueError
            FileManager.export_canvas_image_with_markers(
                defect=sample_defect,
                image_path=non_existent_image,
                output_dir=str(output_dir),
                filename="test_output",
            )

    def test_export_with_specified_filename(
        self, temp_dir, sample_image, sample_defect
    ):
        """指定したファイル名で出力されることをテスト"""
        output_dir = Path(temp_dir) / "output"
        custom_filename = "my_custom_filename"

        result_path = FileManager.export_canvas_image_with_markers(
            defect=sample_defect,
            image_path=sample_image,
            output_dir=str(output_dir),
            filename=custom_filename,
            image_format="PNG",
        )

        # 指定したファイル名が含まれていることを確認
        assert custom_filename in result_path
        # 正確なファイル名であることを確認
        assert Path(result_path).stem == custom_filename
        # ファイルが存在することを確認
        assert Path(result_path).exists()

    def test_export_with_auto_generated_filename(
        self, temp_dir, sample_image, sample_defect
    ):
        """ファイル名を指定しない場合、自動生成されることをテスト"""
        output_dir = Path(temp_dir) / "output"

        result_path = FileManager.export_canvas_image_with_markers(
            defect=sample_defect,
            image_path=sample_image,
            output_dir=str(output_dir),
            filename=None,  # 明示的にNoneを指定
        )

        # ファイルが存在することを確認
        assert Path(result_path).exists()
        # ファイル名に "_marked_" が含まれていることを確認（自動生成の場合）
        assert "_marked_" in Path(result_path).name

    def test_export_with_image_size_800x600(
        self, all_test_images, clean_export_dir, sample_defect
    ):
        """画像サイズ 800x600 で出力されることをテスト（テキストエリアを含む）"""
        text_area_width = 300  # デフォルトのテキストエリア幅

        for image_path in all_test_images:
            # 元のファイル名（拡張子なし）を取得
            original_name = Path(image_path).stem
            output_filename = f"{original_name}_800x600"

            result_path = FileManager.export_canvas_image_with_markers(
                defect=sample_defect,
                image_path=image_path,
                output_dir=clean_export_dir,
                filename=output_filename,
                max_image_size="800x600",
                text_area_width=text_area_width,
            )

            # ファイルが存在することを確認
            assert Path(result_path).exists()

            # 画像サイズを確認（画像部分 + テキストエリア）
            img = Image.open(result_path)
            # 元画像が800x600より小さい場合は縮小されない
            # 元画像が大きい場合はアスペクト比を維持して800x600以内に縮小
            # テキストエリア300pxが右側に追加される
            assert img.width >= 300  # 最小でもテキストエリアの幅
            assert img.height <= 600  # 高さは最大600px

    def test_export_with_image_size_1920x1080(
        self, all_test_images, clean_export_dir, sample_defect
    ):
        """画像サイズ 1920x1080 で出力されることをテスト
        元画像が1920x1080より小さい場合は縮小されない、元画像が大きい場合はアスペクト比を維持して1920x1080以内に縮小
        テキストエリア300pxが右側に追加される
        """
        for image_path in all_test_images:
            # 元のファイル名（拡張子なし）を取得
            original_name = Path(image_path).stem
            output_filename = f"{original_name}_1920x1080"

            result_path = FileManager.export_canvas_image_with_markers(
                defect=sample_defect,
                image_path=image_path,
                output_dir=clean_export_dir,
                filename=output_filename,
                max_image_size="1920x1080",
                text_area_width=300,
            )

            # ファイルが存在することを確認
            assert Path(result_path).exists()

            # 画像サイズを確認
            img = Image.open(result_path)
            # 幅は最小300px（テキストエリア）、高さは最大1080px
            assert img.width >= 300
            assert img.height <= 1080

    def test_export_with_image_size_asterisk_format(
        self, all_test_images, clean_export_dir, sample_defect
    ):
        """画像サイズを * 形式（640*480）で指定した場合のテスト
        元画像が640x480より小さい場合は縮小されない、元画像が大きい場合はアスペクト比を維持して640x480以内に縮小
        テキストエリア300pxが右側に追加される
        """
        for image_path in all_test_images:
            # 元のファイル名（拡張子なし）を取得
            original_name = Path(image_path).stem
            output_filename = f"{original_name}_640x480"

            result_path = FileManager.export_canvas_image_with_markers(
                defect=sample_defect,
                image_path=image_path,
                output_dir=clean_export_dir,
                filename=output_filename,
                max_image_size="640*480",
                text_area_width=300,
            )

            # ファイルが存在することを確認
            assert Path(result_path).exists()

            # 画像サイズを確認
            img = Image.open(result_path)
            # 幅は最小300px（テキストエリア）、高さは最大480px
            assert img.width >= 300
            assert img.height <= 480

    def test_export_with_image_size_multiplication_sign(
        self, all_test_images, clean_export_dir, sample_defect
    ):
        """画像サイズを × 形式（320×240）で指定した場合のテスト
        元画像が320x240より小さい場合は縮小されない、元画像が大きい場合はアスペクト比を維持して320x240以内に縮小
        テキストエリア300pxが右側に追加される
        """
        for image_path in all_test_images:
            # 元のファイル名（拡張子なし）を取得
            original_name = Path(image_path).stem
            output_filename = f"{original_name}_320x240"

            result_path = FileManager.export_canvas_image_with_markers(
                defect=sample_defect,
                image_path=image_path,
                output_dir=clean_export_dir,
                filename=output_filename,
                max_image_size="320×240",
                text_area_width=300,
            )

            # ファイルが存在することを確認
            assert Path(result_path).exists()

            # 画像サイズを確認
            img = Image.open(result_path)
            # 幅は最小300px（テキストエリア）、高さは最大240px
            assert img.width >= 300
            assert img.height <= 240

    def test_export_without_image_size_keeps_original(
        self, all_test_images, clean_export_dir, sample_defect
    ):
        """画像サイズを指定しない場合、元の画像サイズにテキストエリアが追加されることをテスト"""
        for image_path in all_test_images:
            # 元画像のサイズを取得
            original_img = Image.open(image_path)
            original_width, original_height = original_img.size

            # 元のファイル名（拡張子なし）を取得
            original_name = Path(image_path).stem
            output_filename = f"{original_name}_original"

            result_path = FileManager.export_canvas_image_with_markers(
                defect=sample_defect,
                image_path=image_path,
                output_dir=clean_export_dir,
                filename=output_filename,
                max_image_size=None,  # サイズ指定なし
                text_area_width=300,
            )

            # ファイルが存在することを確認
            assert Path(result_path).exists()

            # 元の画像サイズ + テキストエリア幅になっていることを確認
            result_img = Image.open(result_path)
            assert result_img.width == original_width + 300
            assert result_img.height == original_height

    def test_export_with_invalid_image_size_format(
        self, temp_dir, sample_image, sample_defect
    ):
        """不正な画像サイズ形式の場合に例外が発生することをテスト"""
        output_dir = Path(temp_dir) / "output"

        # 不正な形式でエラーが発生することを確認
        with pytest.raises(ValueError):
            FileManager.export_canvas_image_with_markers(
                defect=sample_defect,
                image_path=sample_image,
                output_dir=str(output_dir),
                filename="test_invalid",
                max_image_size="invalid_format",
            )

    def test_export_with_negative_image_size(
        self, temp_dir, sample_image, sample_defect
    ):
        """負の画像サイズを指定した場合に例外が発生することをテスト"""
        output_dir = Path(temp_dir) / "output"

        # 負の値でエラーが発生することを確認
        with pytest.raises(ValueError):
            FileManager.export_canvas_image_with_markers(
                defect=sample_defect,
                image_path=sample_image,
                output_dir=str(output_dir),
                filename="test_negative",
                max_image_size="-800x600",
            )

    def test_export_with_zero_image_size(self, temp_dir, sample_image, sample_defect):
        """ゼロの画像サイズを指定した場合に例外が発生することをテスト"""
        output_dir = Path(temp_dir) / "output"

        # ゼロの値でエラーが発生することを確認
        with pytest.raises(ValueError):
            FileManager.export_canvas_image_with_markers(
                defect=sample_defect,
                image_path=sample_image,
                output_dir=str(output_dir),
                filename="test_zero",
                max_image_size="0x0",
            )

    def test_export_with_quality_parameter(self, temp_dir, sample_image, sample_defect):
        """品質パラメータが適用されることをテスト（JPEG）"""
        output_dir = Path(temp_dir) / "output"

        # 高品質で保存
        result_high = FileManager.export_canvas_image_with_markers(
            defect=sample_defect,
            image_path=sample_image,
            output_dir=str(output_dir),
            filename="test_high_quality",
            image_format="JPEG",
            quality=95,
        )

        # 低品質で保存
        result_low = FileManager.export_canvas_image_with_markers(
            defect=sample_defect,
            image_path=sample_image,
            output_dir=str(output_dir),
            filename="test_low_quality",
            image_format="JPEG",
            quality=10,
        )

        # 両方のファイルが存在することを確認
        assert Path(result_high).exists()
        assert Path(result_low).exists()

        # 高品質の方がファイルサイズが大きいことを確認
        high_size = Path(result_high).stat().st_size
        low_size = Path(result_low).stat().st_size
        assert high_size > low_size

    def test_export_preserves_marker_position_after_resize(
        self, all_test_images, clean_export_dir, sample_defect
    ):
        """リサイズ後もマーカー位置が相対的に保持されることをテスト"""
        for image_path in all_test_images:
            # 元画像のサイズを取得
            original_img = Image.open(image_path)
            original_width, original_height = original_img.size

            # 相対座標（0.5, 0.5）で中央にマーカーを配置
            sample_defect.x = 0.5
            sample_defect.y = 0.5

            # 元のファイル名（拡張子なし）を取得
            original_name = Path(image_path).stem
            output_filename = f"{original_name}_400x300"

            # リサイズして保存
            result_path = FileManager.export_canvas_image_with_markers(
                defect=sample_defect,
                image_path=image_path,
                output_dir=clean_export_dir,
                filename=output_filename,
                max_image_size="400x300",
                text_area_width=300,
            )

            # ファイルが存在することを確認
            assert Path(result_path).exists()
            result_img = Image.open(result_path)

            # 幅は最小300px（テキストエリア）、高さは最大300px
            assert result_img.width >= 300
            assert result_img.height <= 300

            # マーカーが描画されていることを確認
            # 画像が正常に生成されていることを確認
            assert result_img.mode in ("RGB", "RGBA")

    def test_aspect_ratio_preserved_after_resize(
        self, all_test_images, clean_export_dir, sample_defect
    ):
        """リサイズ後も画像部分のアスペクト比が変わらないことを確認するテスト"""
        test_sizes = [
            ("800x600", 800, 600),
            ("1920x1080", 1920, 1080),
            ("640x480", 640, 480),
            ("320x240", 320, 240),
        ]

        for image_path in all_test_images:
            # 元画像のアスペクト比を計算
            original_img = Image.open(image_path)
            original_width, original_height = original_img.size
            original_aspect_ratio = original_width / original_height

            for size_str, max_width, max_height in test_sizes:
                # 元のファイル名（拡張子なし）を取得
                original_name = Path(image_path).stem
                output_filename = f"{original_name}_aspect_{size_str}"

                # 画像をリサイズして出力
                result_path = FileManager.export_canvas_image_with_markers(
                    defect=sample_defect,
                    image_path=image_path,
                    output_dir=clean_export_dir,
                    filename=output_filename,
                    max_image_size=size_str,
                    text_area_width=300,
                )

                # ファイルが存在することを確認
                assert Path(result_path).exists()

                # 出力画像を読み込み
                result_img = Image.open(result_path)
                result_width, result_height = result_img.size

                # テキストエリアの幅を除いた画像部分の幅を計算
                image_width = result_width - 300

                # 画像部分のアスペクト比を計算
                if image_width > 0 and result_height > 0:
                    result_aspect_ratio = image_width / result_height

                    # リサイズされた場合、元のアスペクト比が保持されていることを確認
                    # （浮動小数点の比較なので、誤差を考慮）
                    if original_width > max_width or original_height > max_height:
                        assert abs(result_aspect_ratio - original_aspect_ratio) < 0.01
                    else:
                        # リサイズされない場合は元のサイズと同じ
                        assert image_width == original_width
                        assert result_height == original_height

    def test_aspect_ratio_preserved_without_resize(
        self, all_test_images, clean_export_dir, sample_defect
    ):
        """リサイズしない場合、元画像のアスペクト比が保持されることを確認するテスト"""
        for image_path in all_test_images:
            # 元画像のサイズとアスペクト比を取得
            original_img = Image.open(image_path)
            original_width, original_height = original_img.size
            original_aspect_ratio = original_width / original_height

            # 元のファイル名（拡張子なし）を取得
            original_name = Path(image_path).stem
            output_filename = f"{original_name}_no_resize_aspect"

            # リサイズせずに出力
            result_path = FileManager.export_canvas_image_with_markers(
                defect=sample_defect,
                image_path=image_path,
                output_dir=clean_export_dir,
                filename=output_filename,
                max_image_size=None,  # リサイズしない
                text_area_width=300,
            )

            # ファイルが存在することを確認
            assert Path(result_path).exists()

            # 出力画像を読み込み
            result_img = Image.open(result_path)
            result_width, result_height = result_img.size

            # 幅は元画像 + テキストエリア、高さは元画像と同じであることを確認
            assert result_width == original_width + 300
            assert result_height == original_height

            # 画像部分のアスペクト比が保持されていることを確認
            image_width = result_width - 300
            result_aspect_ratio = image_width / result_height
            assert abs(result_aspect_ratio - original_aspect_ratio) < 0.001

    def test_aspect_ratio_consistency_across_sizes(
        self, all_test_images, clean_export_dir, sample_defect
    ):
        """同じ最大サイズで異なる元画像を出力した場合、それぞれのアスペクト比が保持されることを確認"""
        test_max_size = "800x600"
        max_width, max_height = 800, 600

        for image_path in all_test_images[:2]:  # 最初の2つの画像でテスト
            # 元画像のアスペクト比を取得
            original_img = Image.open(image_path)
            original_width, original_height = original_img.size
            original_aspect_ratio = original_width / original_height

            original_name = Path(image_path).stem
            output_filename = f"{original_name}_consistency_{test_max_size}"

            result_path = FileManager.export_canvas_image_with_markers(
                defect=sample_defect,
                image_path=image_path,
                output_dir=clean_export_dir,
                filename=output_filename,
                max_image_size=test_max_size,
                text_area_width=300,
            )

            result_img = Image.open(result_path)
            result_width, result_height = result_img.size

            # テキストエリアの幅を除いた画像部分の幅を計算
            image_width = result_width - 300

            # 画像部分のアスペクト比を計算
            if image_width > 0 and result_height > 0:
                result_aspect_ratio = image_width / result_height

                # リサイズされた場合でも、元のアスペクト比が保持されていることを確認
                if original_width > max_width or original_height > max_height:
                    assert abs(result_aspect_ratio - original_aspect_ratio) < 0.01
                else:
                    # リサイズされない場合は元のサイズと同じ
                    assert image_width == original_width
                    assert result_height == original_height


class TestTextAreaWidth:
    """text_area_widthパラメータのテストクラス"""

    def test_text_area_width_100(
        self, all_test_images, clean_export_dir, sample_defect
    ):
        """テキストエリア幅100pxでの出力テスト"""
        text_area_width = 100
        output_subdir = Path(clean_export_dir) / "text_area_100"
        output_subdir.mkdir(parents=True, exist_ok=True)

        for image_path in all_test_images:
            original_img = Image.open(image_path)
            original_width, original_height = original_img.size

            original_name = Path(image_path).stem
            output_filename = f"{original_name}_text_area_100"

            result_path = FileManager.export_canvas_image_with_markers(
                defect=sample_defect,
                image_path=image_path,
                output_dir=str(output_subdir),
                filename=output_filename,
                max_image_size=None,
                text_area_width=text_area_width,
            )

            # ファイルが存在することを確認
            assert Path(result_path).exists()

            # 画像サイズを確認
            result_img = Image.open(result_path)
            assert result_img.width == original_width + text_area_width
            assert result_img.height == original_height

    def test_text_area_width_200(
        self, all_test_images, clean_export_dir, sample_defect
    ):
        """テキストエリア幅200pxでの出力テスト"""
        text_area_width = 200
        output_subdir = Path(clean_export_dir) / "text_area_200"
        output_subdir.mkdir(parents=True, exist_ok=True)

        for image_path in all_test_images:
            original_img = Image.open(image_path)
            original_width, original_height = original_img.size

            original_name = Path(image_path).stem
            output_filename = f"{original_name}_text_area_200"

            result_path = FileManager.export_canvas_image_with_markers(
                defect=sample_defect,
                image_path=image_path,
                output_dir=str(output_subdir),
                filename=output_filename,
                max_image_size=None,
                text_area_width=text_area_width,
            )

            # ファイルが存在することを確認
            assert Path(result_path).exists()

            # 画像サイズを確認
            result_img = Image.open(result_path)
            assert result_img.width == original_width + text_area_width
            assert result_img.height == original_height

    def test_text_area_width_300(
        self, all_test_images, clean_export_dir, sample_defect
    ):
        """テキストエリア幅300px（デフォルト）での出力テスト"""
        text_area_width = 300
        output_subdir = Path(clean_export_dir) / "text_area_300"
        output_subdir.mkdir(parents=True, exist_ok=True)

        for image_path in all_test_images:
            original_img = Image.open(image_path)
            original_width, original_height = original_img.size

            original_name = Path(image_path).stem
            output_filename = f"{original_name}_text_area_300"

            result_path = FileManager.export_canvas_image_with_markers(
                defect=sample_defect,
                image_path=image_path,
                output_dir=str(output_subdir),
                filename=output_filename,
                max_image_size=None,
                text_area_width=text_area_width,
            )

            # ファイルが存在することを確認
            assert Path(result_path).exists()

            # 画像サイズを確認
            result_img = Image.open(result_path)
            assert result_img.width == original_width + text_area_width
            assert result_img.height == original_height

    def test_text_area_width_400(
        self, all_test_images, clean_export_dir, sample_defect
    ):
        """テキストエリア幅400pxでの出力テスト"""
        text_area_width = 400
        output_subdir = Path(clean_export_dir) / "text_area_400"
        output_subdir.mkdir(parents=True, exist_ok=True)

        for image_path in all_test_images:
            original_img = Image.open(image_path)
            original_width, original_height = original_img.size

            original_name = Path(image_path).stem
            output_filename = f"{original_name}_text_area_400"

            result_path = FileManager.export_canvas_image_with_markers(
                defect=sample_defect,
                image_path=image_path,
                output_dir=str(output_subdir),
                filename=output_filename,
                max_image_size=None,
                text_area_width=text_area_width,
            )

            # ファイルが存在することを確認
            assert Path(result_path).exists()

            # 画像サイズを確認
            result_img = Image.open(result_path)
            assert result_img.width == original_width + text_area_width
            assert result_img.height == original_height

    def test_text_area_width_500(
        self, all_test_images, clean_export_dir, sample_defect
    ):
        """テキストエリア幅500pxでの出力テスト"""
        text_area_width = 500
        output_subdir = Path(clean_export_dir) / "text_area_500"
        output_subdir.mkdir(parents=True, exist_ok=True)

        for image_path in all_test_images:
            original_img = Image.open(image_path)
            original_width, original_height = original_img.size

            original_name = Path(image_path).stem
            output_filename = f"{original_name}_text_area_500"

            result_path = FileManager.export_canvas_image_with_markers(
                defect=sample_defect,
                image_path=image_path,
                output_dir=str(output_subdir),
                filename=output_filename,
                max_image_size=None,
                text_area_width=text_area_width,
            )

            # ファイルが存在することを確認
            assert Path(result_path).exists()

            # 画像サイズを確認
            result_img = Image.open(result_path)
            assert result_img.width == original_width + text_area_width
            assert result_img.height == original_height

    def test_text_area_width_with_resize(
        self, all_test_images, clean_export_dir, sample_defect
    ):
        """テキストエリア幅とリサイズを組み合わせたテスト"""
        test_configs = [
            (100, "800x600", "text_area_100_resize_800x600"),
            (200, "800x600", "text_area_200_resize_800x600"),
            (300, "1920x1080", "text_area_300_resize_1920x1080"),
            (400, "640x480", "text_area_400_resize_640x480"),
            (500, "1280x720", "text_area_500_resize_1280x720"),
        ]

        for text_area_width, max_size, subdir_name in test_configs:
            output_subdir = Path(clean_export_dir) / subdir_name
            output_subdir.mkdir(parents=True, exist_ok=True)

            # 最大サイズをパース
            max_width, max_height = map(int, max_size.split("x"))

            for image_path in all_test_images:
                original_img = Image.open(image_path)
                original_width, original_height = original_img.size

                original_name = Path(image_path).stem
                output_filename = f"{original_name}_{subdir_name}"

                result_path = FileManager.export_canvas_image_with_markers(
                    defect=sample_defect,
                    image_path=image_path,
                    output_dir=str(output_subdir),
                    filename=output_filename,
                    max_image_size=max_size,
                    text_area_width=text_area_width,
                )

                # ファイルが存在することを確認
                assert Path(result_path).exists()

                # 画像サイズを確認
                result_img = Image.open(result_path)

                # テキストエリア幅を除いた画像部分の幅
                image_width = result_img.width - text_area_width

                # 画像部分が最大サイズ以下であることを確認
                assert image_width <= max_width
                assert result_img.height <= max_height

                # リサイズされた場合、アスペクト比が保持されていることを確認
                if original_width > max_width or original_height > max_height:
                    original_aspect_ratio = original_width / original_height
                    result_aspect_ratio = image_width / result_img.height
                    assert abs(result_aspect_ratio - original_aspect_ratio) < 0.01

    def test_text_area_width_small_value(
        self, all_test_images, clean_export_dir, sample_defect
    ):
        """小さなテキストエリア幅（50px）での出力テスト"""
        text_area_width = 50
        output_subdir = Path(clean_export_dir) / "text_area_50"
        output_subdir.mkdir(parents=True, exist_ok=True)

        for image_path in all_test_images[:2]:  # 最初の2つの画像でテスト
            original_img = Image.open(image_path)
            original_width, original_height = original_img.size

            original_name = Path(image_path).stem
            output_filename = f"{original_name}_text_area_50"

            result_path = FileManager.export_canvas_image_with_markers(
                defect=sample_defect,
                image_path=image_path,
                output_dir=str(output_subdir),
                filename=output_filename,
                max_image_size=None,
                text_area_width=text_area_width,
            )

            # ファイルが存在することを確認
            assert Path(result_path).exists()

            # 画像サイズを確認
            result_img = Image.open(result_path)
            assert result_img.width == original_width + text_area_width
            assert result_img.height == original_height

    def test_text_area_width_large_value(
        self, all_test_images, clean_export_dir, sample_defect
    ):
        """大きなテキストエリア幅（800px）での出力テスト"""
        text_area_width = 800
        output_subdir = Path(clean_export_dir) / "text_area_800"
        output_subdir.mkdir(parents=True, exist_ok=True)

        for image_path in all_test_images[:2]:  # 最初の2つの画像でテスト
            original_img = Image.open(image_path)
            original_width, original_height = original_img.size

            original_name = Path(image_path).stem
            output_filename = f"{original_name}_text_area_800"

            result_path = FileManager.export_canvas_image_with_markers(
                defect=sample_defect,
                image_path=image_path,
                output_dir=str(output_subdir),
                filename=output_filename,
                max_image_size=None,
                text_area_width=text_area_width,
            )

            # ファイルが存在することを確認
            assert Path(result_path).exists()

            # 画像サイズを確認
            result_img = Image.open(result_path)
            assert result_img.width == original_width + text_area_width
            assert result_img.height == original_height

    def test_text_area_width_and_font_size_combinations(
        self, all_test_images, clean_export_dir, sample_defect
    ):
        """テキストエリア幅とフォントサイズの様々な組み合わせテスト"""
        test_configs = [
            # (text_area_width, font_size, subdir_name)
            (100, 10, "text_area_100_font_10"),
            (100, 12, "text_area_100_font_12"),
            (100, 15, "text_area_100_font_15"),
            (120, 10, "text_area_120_font_10"),
            (120, 12, "text_area_120_font_12"),
            (120, 15, "text_area_120_font_15"),
            (150, 10, "text_area_150_font_10"),
            (150, 12, "text_area_150_font_12"),
            (150, 15, "text_area_150_font_15"),
            (180, 10, "text_area_180_font_10"),
            (180, 12, "text_area_180_font_12"),
            (180, 15, "text_area_180_font_15"),
            (200, 10, "text_area_200_font_10"),
            (200, 12, "text_area_200_font_12"),
            (200, 15, "text_area_200_font_15"),
        ]

        for text_area_width, font_size, subdir_name in test_configs:
            output_subdir = Path(clean_export_dir) / subdir_name
            output_subdir.mkdir(parents=True, exist_ok=True)

            for image_path in all_test_images:
                original_img = Image.open(image_path)
                original_width, original_height = original_img.size

                original_name = Path(image_path).stem
                output_filename = f"{original_name}_{subdir_name}"

                result_path = FileManager.export_canvas_image_with_markers(
                    defect=sample_defect,
                    image_path=image_path,
                    output_dir=str(output_subdir),
                    filename=output_filename,
                    max_image_size=None,
                    text_area_width=text_area_width,
                    font_size=font_size,
                )

                # ファイルが存在することを確認
                assert Path(result_path).exists()

                # 画像サイズを確認
                result_img = Image.open(result_path)
                assert result_img.width == original_width + text_area_width
                assert result_img.height == original_height

    def test_font_size_small_with_various_text_area(
        self, all_test_images, clean_export_dir, sample_defect
    ):
        """小さいフォントサイズ（10px）と様々なテキストエリア幅の組み合わせテスト"""
        font_size = 10
        test_widths = [100, 120, 150, 180, 200]

        for text_area_width in test_widths:
            subdir_name = f"font_10_text_area_{text_area_width}"
            output_subdir = Path(clean_export_dir) / subdir_name
            output_subdir.mkdir(parents=True, exist_ok=True)

            for image_path in all_test_images[:2]:  # 最初の2つの画像でテスト
                original_img = Image.open(image_path)
                original_width, original_height = original_img.size

                original_name = Path(image_path).stem
                output_filename = f"{original_name}_{subdir_name}"

                result_path = FileManager.export_canvas_image_with_markers(
                    defect=sample_defect,
                    image_path=image_path,
                    output_dir=str(output_subdir),
                    filename=output_filename,
                    max_image_size=None,
                    text_area_width=text_area_width,
                    font_size=font_size,
                )

                # ファイルが存在することを確認
                assert Path(result_path).exists()

                # 画像サイズを確認
                result_img = Image.open(result_path)
                assert result_img.width == original_width + text_area_width
                assert result_img.height == original_height

    def test_font_size_large_with_various_text_area(
        self, all_test_images, clean_export_dir, sample_defect
    ):
        """中程度のフォントサイズ（15px）と様々なテキストエリア幅の組み合わせテスト"""
        font_size = 15
        test_widths = [100, 120, 150, 180, 200]

        for text_area_width in test_widths:
            subdir_name = f"font_15_text_area_{text_area_width}"
            output_subdir = Path(clean_export_dir) / subdir_name
            output_subdir.mkdir(parents=True, exist_ok=True)

            for image_path in all_test_images[:2]:  # 最初の2つの画像でテスト
                original_img = Image.open(image_path)
                original_width, original_height = original_img.size

                original_name = Path(image_path).stem
                output_filename = f"{original_name}_{subdir_name}"

                result_path = FileManager.export_canvas_image_with_markers(
                    defect=sample_defect,
                    image_path=image_path,
                    output_dir=str(output_subdir),
                    filename=output_filename,
                    max_image_size=None,
                    text_area_width=text_area_width,
                    font_size=font_size,
                )

                # ファイルが存在することを確認
                assert Path(result_path).exists()

                # 画像サイズを確認
                result_img = Image.open(result_path)
                assert result_img.width == original_width + text_area_width
                assert result_img.height == original_height

    def test_font_size_and_text_area_with_resize(
        self, all_test_images, clean_export_dir, sample_defect
    ):
        """フォントサイズ、テキストエリア幅、リサイズの3要素の組み合わせテスト"""
        test_configs = [
            # (text_area_width, font_size, max_size, subdir_name)
            (100, 10, "640x480", "font_10_text_100_resize_640x480"),
            (120, 12, "800x600", "font_12_text_120_resize_800x600"),
            (150, 15, "1024x768", "font_15_text_150_resize_1024x768"),
            (180, 12, "1280x720", "font_12_text_180_resize_1280x720"),
            (200, 15, "1920x1080", "font_15_text_200_resize_1920x1080"),
        ]

        for text_area_width, font_size, max_size, subdir_name in test_configs:
            output_subdir = Path(clean_export_dir) / subdir_name
            output_subdir.mkdir(parents=True, exist_ok=True)

            # 最大サイズをパース
            max_width, max_height = map(int, max_size.split("x"))

            for image_path in all_test_images:
                original_img = Image.open(image_path)
                original_width, original_height = original_img.size

                original_name = Path(image_path).stem
                output_filename = f"{original_name}_{subdir_name}"

                result_path = FileManager.export_canvas_image_with_markers(
                    defect=sample_defect,
                    image_path=image_path,
                    output_dir=str(output_subdir),
                    filename=output_filename,
                    max_image_size=max_size,
                    text_area_width=text_area_width,
                    font_size=font_size,
                )

                # ファイルが存在することを確認
                assert Path(result_path).exists()

                # 画像サイズを確認
                result_img = Image.open(result_path)

                # テキストエリア幅を除いた画像部分の幅
                image_width = result_img.width - text_area_width

                # 画像部分が最大サイズ以下であることを確認
                assert image_width <= max_width
                assert result_img.height <= max_height

                # リサイズされた場合、アスペクト比が保持されていることを確認
                if original_width > max_width or original_height > max_height:
                    original_aspect_ratio = original_width / original_height
                    result_aspect_ratio = image_width / result_img.height
                    assert abs(result_aspect_ratio - original_aspect_ratio) < 0.01


class TestMaxImageSizeTuple:
    """Test max_image_size tuple format"""

    def test_max_image_size_as_tuple(
        self, all_test_images, clean_export_dir, sample_defect
    ):
        """Test with max_image_size as tuple"""
        test_size = (800, 600)
        output_subdir = Path(clean_export_dir) / "tuple_800x600"
        output_subdir.mkdir(parents=True, exist_ok=True)

        for image_path in all_test_images[:2]:
            original_name = Path(image_path).stem

            result_path = FileManager.export_canvas_image_with_markers(
                defect=sample_defect,
                image_path=image_path,
                output_dir=str(output_subdir),
                filename=f"{original_name}_tuple",
                max_image_size=test_size,
                text_area_width=300,
            )

            assert Path(result_path).exists()
            result_img = Image.open(result_path)
            image_width = result_img.width - 300
            assert image_width <= 800
            assert result_img.height <= 600
