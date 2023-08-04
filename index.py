from fastapi import FastAPI
from bs4 import BeautifulSoup
import requests
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
import random


app = FastAPI()

# Configure Cross Origin Resource Sharing (CORS) parameters.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.81 Safari/537.3',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.97 Safari/537.3',
    # Adicione mais User-Agents aqui...
]


@app.get('/search/{loja}/{produto}')
async def search(loja: str, produto: str):
    user_agent = random.choice(USER_AGENTS)
    headers = {
        'User-Agent': user_agent
    }
    url_base = ''
    if loja == 'mercadolivre':
        url_base = f'https://lista.mercadolivre.com.br/'
    elif loja == 'zonasul':
        url_base = f'https://www.zonasul.com.br/'
    elif loja == 'prezunic':
        url_base = f'https://www.prezunic.com.br/'
    elif loja == 'paodeacucar':
        url_base = f'https://www.paodeacucar.com/busca?terms='
    elif loja == 'extra':
        url_base = f'https://www.extra.com.br/{produto}/b'
    elif loja == 'carrefour':
        url_base = f'https://mercado.carrefour.com.br/s?q='
    else:
        return {"error": "Loja não encontrada."}

    result_dict = {
        "loja": loja.capitalize(),
        "produtos": [],
    }
    if loja in ['mercadolivre', 'zonasul', 'prezunic', 'paodeacucar', 'carrefour']:
        response = requests.get(url_base + produto, headers=headers)
    elif loja == ['extra']:
        response = requests.get(url_base)


    response.raise_for_status() # lança uma exceção se houver erro na resposta

    site = BeautifulSoup(response.text, 'html.parser')

    produtos = []
    if loja == 'mercadolivre':
        produtos = site.select('.ui-search-result__wrapper')
    elif loja == 'zonasul':
        produtos = site.select('.vtex-search-result-3-x-galleryItem.vtex-search-result-3-x-galleryItem--small.pa4')
    elif loja == 'prezunic':
        produtos = site.select('.vtex-search-result-3-x-galleryItem.vtex-search-result-3-x-galleryItem--normal.vtex-search-result-3-x-galleryItem--default.pa4')    
    elif loja == 'extra':
        produtos = site.select('div[data-cy="divProduct"]')
    elif loja == 'paodeacucar':
        produtos = site.select('.product-cardstyles__CardStyled-sc-1uwpde0-0.bTCFJV.cardstyles__Card-yvvqkp-0.gXxQWo')
    elif loja == 'carrefour':
        produtos = site.select('li[style="order: 2;"] article')


    for produto in produtos:
        titulo = ''
        link = ''
        preco = ''
        img = ''

        if loja == 'mercadolivre':
            titulo_element = produto.select_one('.ui-search-item__title')
            titulo = titulo_element.text.strip() if titulo_element else 'Produto sem título'
            link_element = produto.select_one('.ui-search-link')
            link = link_element['href'] if link_element else ''
            preco_element = produto.select_one('.ui-search-price__second-line .andes-money-amount__fraction')
            preco = f"R${preco_element.text}" if preco_element else 'Preço não disponível'
            img_element = produto.select_one('.ui-search-result-image__element')
            img = img_element.get('src') if img_element else ''

        elif loja == 'zonasul':
            titulo = produto.find('h2', class_='vtex-product-summary-2-x-productNameContainer mv0 vtex-product-summary-2-x-nameWrapper overflow-hidden c-on-base f5').text.strip()

            link_element = produto.find('a', class_='vtex-product-summary-2-x-clearLink h-100 flex flex-column')
            link = 'https://www.zonasul.com.br' + link_element['href'] if link_element else ''

            preco_element = produto.find('span', class_='zonasul-zonasul-store-0-x-currencyInteger')
            preco_centavos_element = produto.find('span', class_='zonasul-zonasul-store-0-x-currencyFraction')
            preco = f"R${preco_element.text},{preco_centavos_element.text}" if preco_centavos_element else f"R${preco_element.text}"

            img_element = produto.find('img', class_='vtex-product-summary-2-x-imageNormal vtex-product-summary-2-x-image')
            img = img_element['src'] if img_element else ''

        elif loja == 'prezunic':
            titulo_element = produto.select_one('.prezunic-prezunic-components-0-x-ProductName.false')
            titulo = titulo_element.text.strip() if titulo_element else ''

            link_element = produto.select_one('.vtex-product-summary-2-x-clearLink.vtex-product-summary-2-x-clearLink--normal-shelf.h-100.flex.flex-column')
            link = 'https://www.prezunic.com.br'+link_element['href'] if link_element else ''

            real_elements = produto.select('.prezunic-prezunic-components-0-x-currencyInteger')
            real = real_elements[1].text if real_elements else ''

            centavos_element = produto.select('.vtex-store-components-3-x-currencyContainer.vtex-store-components-3-x-currencyContainer--summary .prezunic-prezunic-components-0-x-currencyFraction')
            centavos = centavos_element[1].text if centavos_element else ''

            preco = f"R${real},{centavos}" if centavos else f"R${real}"

            img_tag = produto.select_one('.vtex-product-summary-2-x-imageNormal.vtex-product-summary-2-x-image')
            img = img_tag['src'] if img_tag else None

        elif loja == 'extra':
            titulo = produto.select_one('h3[aria-label]').text.strip()
            link = produto.select_one('a[data-testid="image-with-fallback"]')['href']
            preco = produto.select_one('span[data-testid="price-value"]').text.strip()
            img = produto.select_one('img[data-cy="imageProduct"]')['src']

        elif loja == 'paodeacucar':
            titulo = produto.find('a', class_='product-cardstyles__Link-sc-1uwpde0-9.bSQmwP.hyperlinkstyles__Link-j02w35-0.coaZwR').text
            link = produto.find('a', class_='product-cardstyles__Link-sc-1uwpde0-9.bSQmwP.hyperlinkstyles__Link-j02w35-0.coaZwR')['href']
            preco = produto.find('div', class_='price-tag-normalstyle__LabelPrice-sc-1co9fex-0.lkWvql').text
            img = produto.find('img', class_='product-cardstyles__Image-sc-1uwpde0-3.beZujn')['src']

        elif loja == 'carrefour':
                titulo = produto.select_one('h3 a[data-testid="product-link"]').text.strip()
                link = 'https://mercado.carrefour.com.br' + produto.select_one('h3 a[data-testid="product-link"]')['href']
                preco = produto.select_one('span[data-test-id="price"]').text.strip()
                img = produto.select_one('img[data-product-card-image="true"]')['src']

        produto_dict = {
            'titulo': titulo,
            'link': link,
            'preco': preco,
            'img': img,
            'loja':loja

        }

        result_dict['produtos'].append(produto_dict)

    return result_dict

@app.get('/encarte/{loja}')
async def encarte(loja: str):
    url_base = ''
    if loja == 'guanabara':
        url_base = f'https://www.supermercadosguanabara.com.br/encarte'
    if loja == 'mundial':
        url_base = f'https://www.supermercadosmundial.com.br/encarte'
    else:
        return {"error": "Loja não encontrada."}
    
    result_dict = {
        "loja": loja.capitalize(),
        "encarte": [],
    }

    if loja == 'guanabara':
        response = requests.get(url_base)
        response.raise_for_status()

        site = BeautifulSoup(response.text, 'html.parser')

        div_mae = site.find('div', class_='left')
        link_encarte = div_mae.find('a',class_='button button-save', href=True)['href']
        link = 'https://www.supermercadosguanabara.com.br' + link_encarte

        encarte_dict = {
            'link': link
        }

        result_dict['encarte'].append(encarte_dict)

    if loja == 'mundial':
        response = requests.get(url_base)
        response.raise_for_status()

        site = BeautifulSoup(response.text, 'html.parser')

        div_mae = site.find('div', class_='left')
        link_encarte = div_mae.find('a',class_='button button-save', href=True)['href']
        link = 'https://www.supermercadosguanabara.com.br' + link_encarte

        encarte_dict = {
            'link': link
        }

        result_dict['encarte'].append(encarte_dict)

    return result_dict

if __name__ == "__main__":
    uvicorn.run(app, port=8000)