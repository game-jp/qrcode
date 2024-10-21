import string
from PIL import Image, ImageDraw

# 使用する文字セットを定義
BASE_ALPHABET = string.digits + string.ascii_uppercase + string.ascii_lowercase
EXTRA_ALPHABET = '!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~'
FULL_ALPHABET = BASE_ALPHABET + EXTRA_ALPHABET

# n進数での数値のエンコード
def encode_base_n(number, base):
    if number == 0:
        return FULL_ALPHABET[0]
    encoded = ""
    while number > 0:
        encoded = FULL_ALPHABET[number % base] + encoded
        number //= base
    return encoded

# n進数からのデコード
def decode_base_n(encoded_str, base):
    decoded_value = 0
    for char in encoded_str:
        decoded_value = decoded_value * base + FULL_ALPHABET.index(char)
    return decoded_value

# テキストをエンコードする関数
def text_to_encoded_string(text, chars_per_dot):
    encoded_parts = []
    for char in text:
        if 0 <= ord(char) < 0x10FFFF:
            encoded_char = encode_base_n(ord(char), len(FULL_ALPHABET)).zfill(chars_per_dot)
            encoded_parts.append(encoded_char)
    return ''.join(encoded_parts)

# エンコードされた文字列をRGBピクセルに変換
def encode_large_number_as_pixels(encoded_str, chars_per_dot):
    pixel_values = []
    # 文字列をchars_per_dotごとに分割
    for i in range(0, len(encoded_str), chars_per_dot):
        chunk = encoded_str[i:i + chars_per_dot]
        if len(chunk) < chars_per_dot:
            chunk = chunk.ljust(chars_per_dot, FULL_ALPHABET[0])  # 不足分を埋める
        chunk_value = sum(FULL_ALPHABET.index(char) * (len(FULL_ALPHABET) ** (len(chunk) - j - 1)) for j, char in enumerate(chunk))
        r = (chunk_value // (256 * 256)) % 256
        g = (chunk_value // 256) % 256
        b = chunk_value % 256
        pixel_values.append((r, g, b))
    return pixel_values

# カラフルなQRコードを作成する関数（1x1ピクセル単位）
def create_colored_qr_code(text, img_size=300, chars_per_dot=5):
    encoded_text = text_to_encoded_string(text, chars_per_dot)
    pixel_values = encode_large_number_as_pixels(encoded_text, chars_per_dot)

    total_dots = len(pixel_values)
    side_length = int(total_dots**0.5) + (total_dots % 1)  # 正方形のサイズを計算

    img = Image.new("RGB", (side_length, side_length), "white")  # 正方形の画像を作成
    draw = ImageDraw.Draw(img)

    for i, (r, g, b) in enumerate(pixel_values):
        x = i % side_length
        y = i // side_length
        draw.point((x, y), fill=(r, g, b))  # 各ドットを描画

    return img, side_length, encoded_text

# ピクセルデータを文字列にデコードする関数
def decode_pixels_to_large_number(pixels, chars_per_dot):
    encoded_str = ""
    for r, g, b in pixels:
        chunk_value = (r * 256 * 256) + (g * 256) + b
        encoded_chunk = encode_base_n(chunk_value, len(FULL_ALPHABET)).zfill(chars_per_dot)
        encoded_str += encoded_chunk
    return encoded_str

# テキストをデコードする関数
def encoded_string_to_text(encoded_str, chars_per_dot):
    decoded_chars = []
    for i in range(0, len(encoded_str), chars_per_dot):
        chunk = encoded_str[i:i + chars_per_dot]
        if len(chunk) == chars_per_dot:
            decoded_value = decode_base_n(chunk, len(FULL_ALPHABET))
            if 0 <= decoded_value < 0x110000:
                decoded_chars.append(chr(decoded_value))
    return ''.join(decoded_chars)

# QRコードからデータをデコードする関数
def decode_qr_code(image_path, chars_per_dot):
    img = Image.open(image_path)
    pixels = list(img.getdata())
    
    encoded_str = decode_pixels_to_large_number(pixels, chars_per_dot)
    decoded_text = encoded_string_to_text(encoded_str, chars_per_dot)
    
    return decoded_text

# メイン関数
def main(text, img_size=300, chars_per_dot=5):
    # エンコード
    qr_img, side_length, encoded_text = create_colored_qr_code(text, img_size=img_size, chars_per_dot=chars_per_dot)
    
    qr_img.save("colored_qr_code_square.png")
    print("QRコードを保存しました: colored_qr_code_square.png")
    
    print(f"QRコードのサイズ: {side_length} x {side_length} ドット")
    print(f"エンコードされた文字列: {encoded_text}")
    
    # デコード
    decoded_text = decode_qr_code("colored_qr_code_square.png", chars_per_dot)
    print(f"デコードされた文字列: {decoded_text}")

# 実行
if __name__ == "__main__":
    main("abcdefghijklmnopqrstuvwxyz"*10, chars_per_dot=10)
