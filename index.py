from fastapi import FastAPI
from bs4 import BeautifulSoup
import requests
import uvicorn
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Configure Cross Origin Resource Sharing (CORS) parameters.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get('/search/{loja}/{produto}')
async def search(loja: str, produto: str):
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
    else:
        return {"error": "Loja não encontrada."}

    result_dict = {
        "loja": loja.capitalize(),
        "produtos": [],
    }
    if loja == 'mercadolivre' or 'zonasul' or 'prezunic' or 'paodeacucar' or 'carrefour':
        response = requests.get(url_base + produto)

    response.raise_for_status() # lança uma exceção se houver erro na resposta

    site = BeautifulSoup(response.text, 'html.parser')

    produtos = []
    if loja == 'mercadolivre':
        produtos = site.select('.ui-search-result__wrapper shops__result-wrapper')
    elif loja == 'zonasul':
        produtos = site.select('.vtex-search-result-3-x-galleryItem vtex-search-result-3-x-galleryItem--small pa4')
    elif loja == 'prezunic':
        produtos = site.select('.vtex-search-result-3-x-galleryItem.vtex-search-result-3-x-galleryItem--normal.vtex-search-result-3-x-galleryItem--default.pa4')    
    elif loja == 'extra':
        produtos = site.select('.sc-5fec12f4-0 cxOoNz sc-f86ccf37-1 esRPia')
    elif loja == 'paodeacucar':
        div_mae = site.find('div', class_='MuiGrid-root gridstyles-sc-6scn59-0 kZBCvb MuiGrid-container MuiGrid-spacing-xs-2')
        produtos = div_mae.find('div', class_='MuiGrid-root gridstyles-sc-6scn59-0 dmpXNW MuiGrid-item MuiGrid-grid-xs-12 MuiGrid-grid-sm-6 MuiGrid-grid-md-4 MuiGrid-grid-lg-3 MuiGrid-grid-xl-3')
    elif loja == 'carrefour':
        produtos = site.select(".relative flex flex-col h-full rounded-lg md:rounded-none //// shadow-regular bg-white md:shadow-none md:border md:border[#F2F2F2] pb-0")


    for produto in produtos:
        titulo = ''
        link = ''
        preco = ''
        img = ''

        if loja == 'mercadolivre':
            titulo = produto.select_one('.ui-search-item__title shops__item-title').text
            link = produto.select_one('.ui-search-item__group__element shops__items-group-details ui-search-link')['href']
            real = produto.select_one('.andes-money-amount__fraction').text
            centavos = produto.select_one('.price-tag-cents')
            preco = f"R${real},{centavos.text}" if centavos else f"R${real}"
            img_tag = produto.select_one('.ui-search-link')
            img = img_tag['src'] if img_tag else None

        elif loja == 'zonasul':
            titulo_element = produto.select_one('.vtex-product-summary-2-x-productBrand vtex-product-summary-2-x-brandName t-body')
            titulo = titulo_element.text.strip() if titulo_element else ''

            link_element = produto.select_one('.vtex-product-summary-2-x-clearLink h-100 flex flex-column')
            link = 'https://www.zonasul.com.br'+link_element['href'] if link_element else ''

            real_elements = produto.select('.zonasul-zonasul-store-0-x-currencyInteger')
            real = real_elements[1].text if real_elements else ''

            centavos_element = produto.select('.zonasul-zonasul-store-0-x-currencyFraction')
            centavos = centavos_element[1].text if centavos_element else ''

            preco = f"R${real},{centavos}" if centavos else f"R${real}"

            img_tag = produto.select_one('.vtex-product-summary-2-x-imageNormal vtex-product-summary-2-x-image')
            img = img_tag['src'] if img_tag else None

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
            titulo_element = produto.select_one('.sc-2b5b888e-2 KTGxe')
            titulo = titulo_element.text.strip() if titulo_element else ''

            link_element = produto.select_one('.sc-2b5b888e-1 cflebu')
            link = link_element['href'] if link_element else ''

            real_elements = produto.select('.sc-c0914aad-9 heYWpn')
            real = real_elements[0].text if real_elements else ''

            centavos_element = produto.select(None)
            centavos = centavos_element.text if centavos_element else ''

            preco = f"R${real},{centavos}" if centavos else f"R${real}"

            img_tag = produto.select_one('.sc-d2913f46-0 htwjrw')
            img = img_tag['src'] if img_tag else None

        elif loja == 'paodeacucar':
            titulo = produto.select_one('.product-cardstyles__Link-sc-1uwpde0-9 bSQmwP hyperlinkstyles__Link-j02w35-0 coaZwR').text
            link_element = produto.select_one('.hyperlinkstyles__Link-j02w35-0 hbKsSa')
            link = 'https://www.paodeacucar.com'+link_element['href'] if link_element else ''
            real = produto.select_one('.price-tag-normalstyle__LabelPrice-sc-1co9fex-0 lkWvql').text
            centavos = produto.select_one(None)
            preco = f"R${real},{centavos.text}" if centavos else f"R${real}"
            img_tag = produto.select_one('.product-cardstyles__Image-sc-1uwpde0-3 beZujn')
            img = img_tag['src'] if img_tag else None

        elif loja == 'carrefour':
            titulo = produto.select_one('.add-to-cart__button bg-[#1E5BC6] text-xs md:text-sm uppercase w-full h-[30px] md:h-10 flex items-center justify-center rounded-lg text-xs text-white md:bg-blue-brand md:hover:bg-blue-doger md:uppercase md:text-sm md:rounded-[5px]').text
            link_element = produto.select_one('.add-to-cart__button bg-[#1E5BC6] text-xs md:text-sm uppercase w-full h-[30px] md:h-10 flex items-center justify-center rounded-lg text-xs text-white md:bg-blue-brand md:hover:bg-blue-doger md:uppercase md:text-sm md:rounded-[5px]')
            link = 'https://mercado.carrefour.com.br'+link_element['href'] if link_element else ''          
            real = produto.select_one('.text-base text-blue-royal font-medium').text
            preco = f"R${real}"
            img_tag = produto.select_one('.object-contain')
            img = img_tag['src'] if img_tag else None

        produto_dict = {
            'titulo': titulo,
            'link': link,
            'preco': preco,
            'img': img
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

