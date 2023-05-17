from fastapi import FastAPI
from bs4 import beautifulsoup4
import requests

app = FastAPI()

@app.get('/search/{loja}/{produto}')
async def search(loja: str, produto: str):
    url_base = ''
    if loja == 'mercadolivre':
        url_base = f'https://lista.mercadolivre.com.br/'
    elif loja == 'americanas':
        url_base = f'https://www.americanas.com.br/busca/'
    else:
        return {"error": "Loja não encontrada."}

    result_dict = {
        "loja": loja.capitalize(),
        "produtos": [],
    }

    response = requests.get(url_base + produto)
    response.raise_for_status() # lança uma exceção se houver erro na resposta

    site = beautifulsoup4(response.text, 'html.parser')

    produtos = []
    if loja == 'mercadolivre':
        produtos = site.select('.ui-search-result__content-wrapper.shops__result-content-wrapper')
    elif loja == 'americanas':
        produtos = site.select('.product-grid-item')

    for produto in produtos:
        titulo = ''
        link = ''
        preco = ''
        img = ''

        if loja == 'mercadolivre':
            titulo = produto.select_one('.ui-search-item__title.shops__item-title').text
            link = produto.select_one('.ui-search-item__group__element.shops__items-group-details.ui-search-link')['href']
            real = produto.select_one('.price-tag-fraction').text
            centavos = produto.select_one('.price-tag-cents')
            preco = f"R${real},{centavos.text}" if centavos else f"R${real}"
            img_tag = produto.select_one('.ui-search-result-image__element.shops__image-element')
            img = img_tag['src'] if img_tag else None
        elif loja == 'americanas':
            titulo = produto.select_one('.product-grid-item .product-card .product-card--title').text.strip()
            link = produto.select_one('.product-grid-item .product-card a')['href']
            preco = produto.select_one('.product-grid-item .product-card .product-card--price .value').text

        produto_dict = {
            'titulo': titulo,
            'link': link,
            'preco': preco,
            'img': img
        }

        result_dict['produtos'].append(produto_dict)

    return result_dict