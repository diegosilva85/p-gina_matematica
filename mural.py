from PIL import Image, ImageFont, ImageDraw

font_caminho = "./fonts/LiberationSans-Regular.ttf"


class Mural:
    def __init__(self, turma: str, prova: str, media: float, moda: int, mediana: float, desvio: float, pm: float,
                 ouro: list,
                 prata: list, bronze: list):
        self.mural = Image.open("./static/Mural.png")
        draw = ImageDraw.Draw(self.mural)
        font = ImageFont.truetype(font=font_caminho, size=24)
        header = f'MURAL {turma.upper()}'
        # Escreve o Cabeçalho
        draw.text((400, 20), header, fill='black', font=font)
        draw.text((390, 50), text=f"{prova}º SEMANA", fill='black', font=font)
        x_feedback = 640
        y_feedback = 110
        # Escreve as estatísticas
        draw.text((x_feedback, y_feedback), text='DESEMPENHO DA TURMA', fill='black', font=font)
        draw.text((x_feedback, y_feedback + 30), text=f"MÉDIA = {media}", fill='black', font=font)
        draw.text((x_feedback, y_feedback + 60), text=f"MODA = {moda}", fill='black', font=font)
        draw.text((x_feedback, y_feedback + 90), text=f"MEDIANA = {mediana}", fill='black', font=font)
        draw.text((x_feedback, y_feedback + 120), text=f"DESVIO-PADRÃO = {desvio}", fill='black', font=font)
        draw.text((x_feedback, y_feedback + 150), text=f"PM MÉDIO = {pm}", fill='black', font=font)
        draw.line([(x_feedback - 10, 100), (950, 100), (950, 290), (x_feedback - 10, 290), (x_feedback - 10, 100)],
                  fill='black', width=2)
        x_top, y_top = 10, 10
        x_bottom, y_bottom = 973, 952
        draw.line([(x_top, y_top), (x_bottom, y_top), (x_bottom, y_bottom), (x_top, y_bottom), (x_top, y_top)],
                  fill='black', width=2)
        lista_ouro = ouro
        x_gold = 370
        y_gold = 380
        for nome in lista_ouro:
            draw.text((x_gold, y_gold), text=nome, fill='black', font=font)
            y_gold += 30
        lista_prata = prata
        x_silver = 70
        y_silver = 620
        for nome_pr in lista_prata:
            draw.text((x_silver, y_silver), text=nome_pr, fill='black', font=font)
            y_silver += 30
        lista_bronze = bronze
        x_bronze = 710
        y_bronze = 690
        for nome_br in lista_bronze:
            draw.text((x_bronze, y_bronze), text=nome_br, fill='black', font=font)
            y_bronze += 30
        self.caminho = f"./static/mural_{turma}_{prova}.png"
        self.caminho_static = f"mural_{turma}_{prova}.png"
        self.mural.save(self.caminho)
