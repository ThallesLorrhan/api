from fastapi import FastAPI
from bs4 import BeautifulSoup
import requests
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
import random
from lxml import html

app = FastAPI()

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
    elif loja == 'carrefour':
        url_base = f'https://mercado.carrefour.com.br/s?q='
    elif loja == 'redesuperbom':
        url_base = f'https://www.redesuperbom.com.br/busca/?q='
    elif loja == 'superprix':
        url_base = f'https://www.superprix.com.br/'
    elif loja == 'atacadao':
        url_base = f'https://www.atacadao.com.br/catalogo/?queryString='
    else:
        return {"error": "Loja não encontrada."}

    result_dict = {
        "loja": loja.capitalize(),
        "produtos": [],
    }
    if loja in ['mercadolivre', 'prezunic', 'paodeacucar', 'carrefour', 'redesuperbom', 'superprix', 'atacadao']:
        response = requests.get(url_base + produto, headers=headers)
        site = BeautifulSoup(response.text, 'html.parser')
    elif loja in ['zonasul']:
        response = requests.get(url_base + produto, headers=headers)
        site = html.fromstring(response.content)

    
        
    response.raise_for_status() # lança uma exceção se houver erro na resposta

    
    


    produtos = []
    if loja == 'mercadolivre':
        produtos = site.select('.ui-search-result__wrapper')
    if loja == 'zonasul':
        produtos = site.cssselect('.vtex-search-result-3-x-galleryItem')
    elif loja == 'prezunic':
        produtos = site.select('.vtex-search-result-3-x-galleryItem.vtex-search-result-3-x-galleryItem--normal.vtex-search-result-3-x-galleryItem--default.pa4')    
    elif loja == 'paodeacucar':
        produtos = site.select('div', class_='product-cardstyles__Card-sc-1uwpde0-6')
    elif loja == 'carrefour':
        produtos = site.select('li[style="order: 1;"] article')
    elif loja == 'redesuperbom':
        produtos = site.select('.item-produto')
    elif loja == 'superprix':
        produtos = site.select('li', class_='mercearia-|-superprix-supermercado-online ok')
    elif loja == 'atacadao':
        produtos = site.select('div', class_='product-box')
        

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
            titulo_element = produto.cssselect('.vtex-product-summary-2-x-productBrand')[0]
            preco_element = produto.cssselect('.zonasul-zonasul-store-0-x-currencyInteger')[0]
            decimal_element = produto.cssselect('.zonasul-zonasul-store-0-x-currencyDecimal')[0]
            imagem_element = produto.cssselect('.vtex-product-summary-2-x-image')[0]
            link_element = produto.cssselect('.vtex-product-summary-2-x-clearLink')[0]

            titulo = titulo_element.text_content().strip()
            preco = f"R$ {preco_element.text_content().strip()}"
            img = imagem_element.get('src')
            link = 'https://www.zonasul.com.br' + link_element.get('href')
            

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

        elif loja == 'paodeacucar':
            titulo_element = produto.select_one('.product-cardstyles__Link-sc-1uwpde0-9.bSQmwP.hyperlinkstyles__Link-j02w35-0.coaZwR')
            titulo = titulo_element.text.strip() if titulo_element else 'Produto sem título'
            link_element = produto.select_one('.hyperlinkstyles__Link-j02w35-0.hbKsSa')
            link = 'https://www.paodeacucar.com/' + link_element['href'] if link_element else ''
            preco_element = produto.select_one('.price-tag-normalstyle__LabelPrice-sc-1co9fex-0.lkWvql')
            preco = f"R${preco_element.text.replace('R$', '').strip()}" if preco_element else 'Preço não disponível'
            img_element = produto.select_one('.product-cardstyles__Image-sc-1uwpde0-3.beZujn')
            img = img_element.get('src') if img_element else ''

        elif loja == 'carrefour':
            titulo_element = produto.select_one('h3 span.overflow-hidden.text-ellipsis.-webkit-box.-webkit-line-clamp-3.-webkit-box-orient-vertical.text-[13px].text-monet-400 a')
            titulo = titulo_element['title'] if titulo_element else 'Produto sem título'
            produto["titulo"] = titulo

            link_element = produto.select_one('h3 span.overflow-hidden.text-ellipsis.-webkit-box.-webkit-line-clamp-3.-webkit-box-orient-vertical.text-[13px].text-monet-400 a')
            link = link_element['href'] if link_element else ''
            produto["link"] = link

            preco_element = produto.select_one('span.text-base.text-blue-royal.font-medium')
            preco = preco_element.text.strip() if preco_element else 'Preço não disponível'
            produto["preco"] = preco

            img_element = produto.select_one('div[data-product-card-image="true"] img')
            img = img_element['src'] if img_element else ''
            produto["img"] = img

            produto["loja"] = loja.lower()

            result_dict["produtos"].append(produto)
            
        elif loja == 'redesuperbom':
                titulo_element = produto.select_one('.item-produto__name')
                titulo = titulo_element.text.strip() if titulo_element else 'Produto sem título'
                link_element = produto.select_one('.item-produto__inner.js-product.js-trk-select-content.js-show-over-add')
                link = 'https://www.redesuperbom.com.br/' + link_element['href'] if link_element else ''
                preco_element = produto.select_one('.item-produto__price-por')
                preco = f"R${preco_element.text.replace('R$', '').strip()}" if preco_element else 'Preço não disponível'
                img_element = produto.select_one('.item-produto__img-main.lazyload')
                img = img_element.get('src') if img_element else ''

        elif loja == 'superprix':
                titulo_element = produto.select_one('h3 a')
                titulo = titulo_element.text.strip() if titulo_element else 'Produto sem título'
                
                link_element = produto.select_one('a.productImage')
                link = link_element['href'] if link_element else ''
                
                preco_element = produto.select_one('div.newPrice--fake')
                preco = f"R${preco_element.text.replace(',', '.').strip()}" if preco_element else 'Preço não disponível'
                
                img_element = produto.select_one('img.productImage')
                img = img_element['src'] if img_element else ''

        elif loja == 'atacadao':
                titulo_element = produto.find('h2', class_='product-box__name')
                titulo = titulo_element.text.strip() if titulo_element else "Título não encontrado"
                
                preco_element = produto.find('span', class_='js-product-box__price')
                preco = preco_element.text.strip() if preco_element else "Preço não encontrado"
                
                img_element = produto.find('img')
                img = img_element['src'] if img_element else "Imagem não encontrada"

        produto_dict = {
            'titulo': titulo,
            'link': link,
            'preco': preco,
            'img': img,
            'loja':loja
        }

        result_dict['produtos'].append(produto_dict)

    return result_dict

if __name__ == "__main__":
    uvicorn.run(app, port=8000)