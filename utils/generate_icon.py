"""
Script para gerar ícone .ico com fundo transparente e proporções corretas.
A imagem é centralizada em um canvas quadrado mantendo a transparência.
"""
from PIL import Image


def create_square_icon(input_path: str, output_path: str) -> None:
    """
    Cria um ícone .ico quadrado a partir de uma imagem,
    centralizando-a e mantendo a transparência.
    """
    # Abrir a imagem original preservando transparência
    img = Image.open(input_path).convert("RGBA")
    
    width, height = img.size
    print(f"Dimensões originais: {width}x{height}")
    
    # Determinar o tamanho do canvas quadrado (maior dimensão)
    max_size = max(width, height)
    
    # Criar canvas quadrado transparente
    square_img = Image.new("RGBA", (max_size, max_size), (0, 0, 0, 0))
    
    # Calcular posição para centralizar a imagem
    x_offset = (max_size - width) // 2
    y_offset = (max_size - height) // 2
    
    # Colar a imagem original no centro (preservando transparência)
    square_img.paste(img, (x_offset, y_offset), img)
    
    print(f"Novo canvas quadrado: {max_size}x{max_size}")
    
    # Criar múltiplas resoluções para o ícone
    sizes = [(256, 256), (128, 128), (64, 64), (48, 48), (32, 32), (16, 16)]
    
    icons = []
    for size in sizes:
        resized = square_img.resize(size, Image.Resampling.LANCZOS)
        icons.append(resized)
    
    # Salvar como .ico com múltiplas resoluções
    icons[0].save(
        output_path,
        format="ICO",
        sizes=[(s, s) for s, _ in sizes],
        append_images=icons[1:]
    )
    
    print(f"Ícone salvo em: {output_path}")


if __name__ == "__main__":
    # Você precisa colocar o arquivo PNG aqui
    # Por exemplo: "rt_counter_original.png"
    input_file = "rt_counter_original.png"
    output_file = "ico.ico"
    
    create_square_icon(input_file, output_file)
