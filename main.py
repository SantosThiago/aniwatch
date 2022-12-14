import requests as r
import json
import query
from bs4 import BeautifulSoup

def get_Links(anime_Name):
    anime_Name = anime_Name.replace(' ', '+')
    sites = ['https://subanimes.cc/', 'https://betteranime.net/']
    urls = []
    result = []

    for site in sites:
        if site == 'https://betteranime.net/':
            url = site + 'pesquisa?titulo=' + anime_Name + '&searchTerm=' + anime_Name
        else:
            url = site + '?s=' + anime_Name

        urls.append(url)
    for url in urls:
        req = r.get(url)
        content = req.content
        soup = BeautifulSoup(content, 'html.parser')
        for elem in soup.findAll('a', href=True):
            if 'https://subanimes.cc/anime/' in elem['href']:
                result.append(elem['href'])

            elif 'https://betteranime.net/anime/' in elem['href']:
                result.append(elem['href'])

            elif 'https://betteranime.net/filme/' in elem['href']:
                result.append(elem['href'])

    return result

def checkLinks(links,names):
    romaji=names[0].replace(' ','+')
    if names[1]!=None:
        english=names[1].replace(' ','%20')
    else:
        english=romaji

    streaming_Names=['netflix','hbomax','amazon','crunchyroll']
    streamings=[]
    for elem in links:
        url=elem['url']
        split=elem['url'].split('.')
        split2=elem['url'].split('//')
        name=split[1]
        name2=split2[1]
        split2=name2.split('/')
        name2=split2[0]
        split2=name2.split('.')
        name2=split2[0]
        if name in streaming_Names:
            result=r.get(url)
            content=result.content
            soup=BeautifulSoup(content,'html.parser')
            title=str(soup.title.string)
            result.close()
            if name=='netflix' or name=='hbomax':
                if len(title)>7:
                    streamings.append([name,url])

            elif name=='amazon':
                search='https://www.primevideo.com/search/ref=atv_nb_sr?phrase='+romaji+'&ie=UTF8'
                req= r.get(search)
                content2=req.content
                soup2=BeautifulSoup(content2,'html.parser')
                flag=0
                for elem in soup2.find('p'):
                    if elem[0]=='W':
                        flag=1

                for elem2 in soup2.findAll('a', href=True):
                    if '/detail/' in elem2['href'] and flag==0:
                        newUrl='https://www.primevideo.com/'+elem2['href']
                        streamings.append(['primevideo',newUrl])
                        flag=1

            elif name=='crunchyroll':
                streamings.append(['crunchyroll',url])

        if name2 == 'crunchyroll':
            streamings.append(['crunchyroll', url])

    return streamings

def findAnimes(url,query,variables):

    resp = r.post(url, json={'query': query, 'variables': variables})
    resp_dic = resp.json()
    infos = resp_dic['data']['Page']['media']
    out=['MANGA','ONE_SHOT','NOVEL','MUSIC']
    for elem in infos:
        form=elem['format']
        if form not in out and 'Hentai' not in elem['genres']:
            romaji = elem['title']['romaji']
            english = elem['title']['english']
            print('Nome:', romaji)
            print('Alternativo:', english)
            print('G??neros:', elem['genres'])
            print('Formato:',form)
            print('Voc?? pode assistir em:')
            streamings = checkLinks(elem['externalLinks'],[romaji,english])
            if streamings != []:
                for streaming in streamings:
                    print(streaming)

            else:
                print('N??o h?? streamings dispon??veis')

            print('\n')

if __name__ == '__main__':
    animes_url=[]
    query = '''
        query ($id: Int, $page: Int, $perPage: Int, $search: String) 
        {
            Page (page: $page, perPage: $perPage) 
            {
                pageInfo 
                {
                    total
                    currentPage
                    lastPage
                    hasNextPage
                    perPage
                    
                }
                media (id: $id, search: $search) 
                {
                    format
                    id
                    title
                    {
                        romaji,
                        english
                    }
                    genres
                    externalLinks
                    {
                        url
                    }
                }
            }
        }
    '''
    url = 'https://graphql.anilist.co'
    while True:
        print('Digite o nome do anime que deseja pesquisar:')
        anime_Name=input()

        if anime_Name=='-1':
            break

        variables = {
            'search': anime_Name
        }
        findAnimes(url,query,variables)
        print('Streamings alternativos:')
        animes_url = get_Links(anime_Name)
        if animes_url != []:
            for anime in animes_url:
                print(anime, '\n')

        else:
            print('N??o h?? animes dispon??veis para esssa pesquisa')