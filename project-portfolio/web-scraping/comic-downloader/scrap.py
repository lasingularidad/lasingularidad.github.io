from pathlib import Path
import shutil

from bs4 import BeautifulSoup
from PIL import Image
import requests


def downloadComic(comic_name, comic_url):
    response = requests.get(comic_url)
    if response.status_code == 200:
        targetDir = Path(comic_name)
        targetDir.mkdir(exist_ok=True)

        soup = BeautifulSoup(response.content, 'html.parser')
        listChapterDiv = soup.find('div', attrs={'class': 'list-chapter'})
        volumeLinkList = listChapterDiv.find_all('a')

        for volLink in volumeLinkList:
            vURL = volLink.attrs['href']
            vName = vURL.split('/')[-1]
            volumeDir = targetDir / vName
            print(f'Downloading pages for volume: {vName}')
            downloadVolume(vURL + '/all', volumeDir)
            buildCBZ(volumeDir)


def downloadVolume(volume_url: str, volume_dir: Path):

    response = requests.get(volume_url)
    if response.status_code == 200:
        volume_dir.mkdir(exist_ok=True)

        soup = BeautifulSoup(response.content, 'html.parser')

        pageDivs = soup.find_all(attrs={'class': 'page-chapter'})
        for div in pageDivs:
            pageName = div.attrs['id']
            pageNum = int(pageName[5:])

            print(f'Downloading image: {pageName}')
            imgTag = div.find('img')
            imgURL = imgTag.attrs['data-original']
            downloadImage(imgURL, volume_dir / f'page{pageNum:04}')


def downloadImage(target_url: str, out_path: Path) -> None:
    imgRequest = requests.get(target_url, stream=True)
    if imgRequest.status_code == 200:
        image = Image.open(imgRequest.raw)
        if image.format == 'JPEG':
            imgExtension = '.jpg'
        elif image.format == 'PNG':
            imgExtension = '.png'
        elif image.format == "WEBP":
            imgExtension = '.webp'
        else:
            raise ValueError(f'Unsupported image format: {image.format}')
        image.save(out_path.with_suffix(imgExtension))
    else:
        raise ConnectionError(f'Error requesting image with url "{target_url}". '
                              f'Response code: {imgRequest.status_code}')


def buildCBZ(target_dir):
    print(f'Compressing folder: {target_dir}')
    shutil.make_archive(target_dir, 'zip', target_dir)
    cbzFileName = target_dir.with_suffix('.zip')
    cbzFileName.rename(cbzFileName.with_suffix('.cbz'))


if __name__ == '__main__':

    target = 'blitz'
    targetURL = f'https://readcomicsfree.net/comic/{target}'

    downloadComic(target, targetURL)

