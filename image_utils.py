import io
import os
from pathlib import Path

from PIL import Image


def convert_to_8bit_bmp(input_path: str, output_path: str) -> bool:
    """
    Converte uma imagem JPG ou PNG para BMP de 8 bits

    Args:
        input_path: Caminho da imagem de entrada (JPG ou PNG)
        output_path: Caminho onde salvar a imagem BMP convertida

    Returns:
        bool: True se a conversão foi bem sucedida, False caso contrário
    """
    try:
        # Abre a imagem
        with Image.open(input_path) as img:
            # Converte para modo 8-bit (paleta de cores)
            if img.mode not in ("L", "P"):  # L = grayscale, P = palette
                # Primeiro converte para RGB se necessário
                if img.mode != "RGB":
                    img = img.convert("RGB")

                # Converte para 8-bit usando paleta de cores
                img = img.convert("P", palette=Image.ADAPTIVE, colors=256)

            # Salva como BMP
            img.save(output_path, "BMP")
            return True
    except Exception as e:
        print(f"Erro ao converter imagem: {e}")
        return False


def convert_to_8bit_bmp_from_bytes(image_data: bytes, output_path: str) -> bool:
    """
    Converte dados de imagem diretamente para BMP de 8 bits

    Args:
        image_data: Dados binários da imagem
        output_path: Caminho onde salvar a imagem BMP convertida

    Returns:
        bool: True se a conversão foi bem sucedida, False caso contrário
    """
    try:
        # Abre a imagem a partir dos dados binários
        img = Image.open(io.BytesIO(image_data))

        # Converte para modo 8-bit (paleta de cores)
        if img.mode not in ("L", "P"):  # L = grayscale, P = palette
            # Primeiro converte para RGB se necessário
            if img.mode != "RGB":
                img = img.convert("RGB")

            # Converte para 8-bit usando paleta de cores
            img = img.convert("P", palette=Image.ADAPTIVE, colors=256)

        # Salva como BMP
        img.save(output_path, "BMP")
        return True
    except Exception as e:
        print(f"Erro ao converter imagem: {e}")
        return False


def convert_image_to_8bit_bmp(input_path: str, output_dir: str = None) -> str:
    """
    Converte uma imagem JPG ou PNG para BMP de 8 bits e retorna o caminho do arquivo convertido

    Args:
        input_path: Caminho da imagem de entrada (JPG ou PNG)
        output_dir: Diretório onde salvar a imagem convertida (padrão: mesmo diretório da entrada)

    Returns:
        str: Caminho do arquivo BMP convertido ou None se falhar
    """
    input_path = Path(input_path)

    if not input_path.exists():
        return None

    if output_dir is None:
        output_dir = input_path.parent
    else:
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

    # Gera o nome do arquivo de saída
    output_filename = input_path.stem + "_8bit.bmp"
    output_path = output_dir / output_filename

    success = convert_to_8bit_bmp(str(input_path), str(output_path))

    if success:
        return str(output_path)
    else:
        return None
