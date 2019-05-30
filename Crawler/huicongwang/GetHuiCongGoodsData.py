import ssl
import bs4
import requests
import os
import time
#数据保存目录
save_img_home = ''
os.makedirs(save_img_home, exist_ok=True)

def write_img(imgurl, saveDirect):
    #print(imgurl)
    r = requests.get("http://"+imgurl)
    with open(saveDirect, 'wb') as f:
        f.write(r.content)


def write_content_text(file_name, contents):
    fh = open(file_name, 'w')
    fh.write(contents)
    fh.close()

def prepare_save_img(main_dir, secon_dir, img_index, last_url):
    main_img_dir_name = main_dir + secon_dir
    os.makedirs(main_img_dir_name, exist_ok=True)
    file_url = main_img_dir_name + '/' + str(img_index) + ".png"
    write_img(last_url, file_url)

def analysis_html(goods_url):
    context = ssl._create_unverified_context()
    user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36"
    get_data = requests.get(goods_url, headers={"User-Agent": user_agent,
                                               'Accept': 'text/html;q=0.9,*/*;q=0.8',
                                               'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
                                               'Accept-Encoding': 'GBK,utf-8;q=0.7,*;q=0.3',
                                               'Connection': 'close',
                                               'Referer': None}).text
    html = bs4.BeautifulSoup(get_data)
    outer_div = html.find('div', {'class': 'Box1Left'})
    goods_detail = html.find('div',id='pdetail')
    main_dir = ''
    goods_info = '商品链接：' + goods_url + '\r\n'
    #1、获取商品标题、主图、价格
    for child in outer_div.children:
        child_type = type(child)
        if str(child_type) == "<class 'bs4.element.Tag'>":
            class_name = child['class'][0]
            #1.1、获取商品标题
            if str(class_name) == 'proTitCon':
                h1_tag = child.find('h1',id='comTitle')
                goods_name = h1_tag.text
                main_dir = save_img_home + goods_name
                goods_info += '商品名称：'+ goods_name + '\r\n'
            #1.2、获取商品的主图
            if str(class_name) == 'Box1LeftCon':
                goods_main_img_div = child.find('div',id='dt-tab')
                ul_tag = goods_main_img_div.find('ul',id="thumblist")
                img_index = 1
                for li in ul_tag.children:
                    li_type = type(li)
                    if str(li_type) == "<class 'bs4.element.Tag'>":
                        img_tag = li.find('a')
                        json_data = img_tag['rel']
                        img_url = str(json_data[4])
                        new_url = img_url.replace("'",'')
                        lenth = len(new_url)
                        full_url = new_url[2:lenth - 1]
                        img_type = 'jpg'
                        if 'png' in full_url:
                            img_type = 'png'
                        last_url = full_url + "..400x400."+img_type;
                        #print("主图的URL："+last_url)
                        #保存图片
                        prepare_save_img(main_dir, '/主图', img_index, last_url)
                        time.sleep(0.05)
                        img_index+=1
            #1.3、获取商品的价格
            if str(class_name) == 'detail-right-con':
                goods_price_div = child.find('div',{'class': 'topPriceRig'})
                goods_price = goods_price_div.text.strip()
                goods_info += "\r\b\r\n"
                goods_info += '商品价格：' + goods_price + '\r\n'
    #2、获取商品的详情
     #2.1获取基本参数
    basic_param = goods_detail.children
    goods_info += "\r\b\r\n"
    goods_info += "商品基本参数：\r\n"
    for para in basic_param:
        para_type = type(para)
        if str(para_type) == "<class 'bs4.element.Tag'>":
            t = para['class']
            class_name = str("".join(t))
            if class_name == 'd-vopyparameter':
                #print(para)
                ul_tag = para.find('ul')
                for li in ul_tag.children:
                    li_type = type(li)
                    if str(li_type) == "<class 'bs4.element.Tag'>":
                        goods_info += "-----"+li.find('span').text+'：'+li.find('p').text + '\r\n'
     #2.2、获取商品详情信息
    goods_detail_info = goods_detail.find('div',id='introduce')
    goods_detail_info_desc = goods_detail_info.text.strip()
    desc_len = len(goods_detail_info_desc)
    #分两种情况，商品详情全部为图片，有图片有文字
    # 商品详情都是图片
    if  desc_len == 0:
        goods_detail_info_desc_s_index = 1
        for goods_detail_info_desc_s in goods_detail_info.children:
            tags_type  = goods_detail_info_desc_s
            children_number = len(list(goods_detail_info_desc_s.children))
            #1、标签内直接是img 标签的
            if 'img' in str(tags_type) and children_number == 0:
                #print('执行了都是img标签的')
                img_url_first = goods_detail_info_desc_s['src']
                filter_img_url_first = img_url_first[2:len(img_url)]
                prepare_save_img(main_dir, '/商品详情图', goods_detail_info_desc_s_index, filter_img_url_first)
                time.sleep(0.05)
                goods_detail_info_desc_s_index += 1
            else:
                imgs = goods_detail_info_desc_s.find_all('img')
                if len(imgs) > 0:
                    #1、获取商品详情大图
                    goods_detail_img_index = 1
                    for img in imgs:
                        img_url = img['src']
                        #print(img_url)
                        filter_img_url = img_url[2:len(img_url)]
                        prepare_save_img(main_dir, '/商品详情图', goods_detail_img_index, filter_img_url)
                        time.sleep(0.05)
                        goods_detail_img_index += 1
        goods_info += "\r\b"
        goods_info += "商品详情文字描述：" + '\r\n' + '----- 该商品详情，都是图片！！！'
    else: #详情有图片，有文字
        goods_info += "\r\b"
        deatil_desc = goods_detail_info.text.strip()
        goods_info += "商品详情文字描述：" +'\r\n' + deatil_desc
        detail_imgs = goods_detail_info.find_all('img')
        goods_detail_img_index_else = 1
        #保存图片
        for img in detail_imgs:
            detail_imgs_img_url = img['src']
            detail_imgs_img_filter_url = detail_imgs_img_url[2:len(detail_imgs_img_url)];
            prepare_save_img(main_dir, '/商品详情图', goods_detail_img_index_else, detail_imgs_img_filter_url)
            time.sleep(0.05)
            goods_detail_img_index_else += 1
    introduce_file = main_dir + '/介绍.txt'
    write_content_text(introduce_file, goods_info)

if __name__ == '__main__':
    goods_url_list = {'https://b2b.hc360.com/supplyself/682301753.html',
                        'https://b2b.hc360.com/supplyself/674558158.html',
                        'https://b2b.hc360.com/supplyself/590554248.html',
                        'https://b2b.hc360.com/supplyself/674912350.html'}
    # goods_url_list = { 'https://b2b.hc360.com/supplyself/590554248.html'}
    print('爬取数据开始：'+str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())))
    for good_url in goods_url_list:
        analysis_html(good_url)
        print(good_url + '：链接数据爬取完毕。')
    print("爬取数据完毕："+str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())))