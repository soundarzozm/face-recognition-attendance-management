let btnDownload = document.querySelector('button');
let img = document.querySelector('img');

btnDownload.addEventListener('click', () =>{
    let imgPath = img.getAttribute('src');
    let fileName = 'test.jpeg';

    saveAs(imgPath, fileName);
})
