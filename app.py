from flask import request, render_template, Flask, jsonify
from flask_cors import CORS,cross_origin #To make the server available across countries
import requests
from bs4 import BeautifulSoup as bs
from urllib.request import urlopen 
import pymongo
import logging

logging.basicConfig(filename= 'webScrap.log', level= logging.INFO)
app = Flask(__name__)

@app.route('/' ,methods = ['GET'])
def index_page():
    return render_template('index.html')

@app.route('/review', methods=['GET', 'POST'])
def scrapping():
    if request.method=='POST':
        try:
            keyword = request.form['content'].replace(" ","")
            flipkart_link = "https://www.flipkart.com/search?q="+ keyword
            flipKart_page = urlopen(flipkart_link)
            flipkart_html = bs(flipKart_page.read(), 'html.parser')
            product_list=flipkart_html.find_all("div",{"class":"_1AtVbE col-12-12"})
            del product_list[0:2]
            product = product_list[0]
            product_link="https://www.flipkart.com"+product.div.div.div.a['href']
            prod_sc=requests.get(product_link)
            prod_html= bs(prod_sc.text,"html.parser")
            prod_comm_list = prod_html.find_all("div",{"class":"col _2wzgFH"})
            reviews=[]
            for i in prod_comm_list:
                try:
                    ratings=i.div.div.text
                except Exception as e:
                    print("Exception in rating module")
                try: 
                    comments_list = i.find_all("div",{"class":"t-ZTKy"})[0].div.text
                except Exception as e:
                    print("Exception in comments module")
                try:    
                    names_list=i.find_all("div",{"class":"row _3n8db9"})[0].div.p.text
                except Exception as e:
                    print("Exception in name module")

                customer_review={'name':names_list,'rating':ratings,'comment':comments_list}
                reviews.append(customer_review)
            client=pymongo.MongoClient("mongodb+srv://hariprasanthsanthanam:shp13111995@cluster0.2aizdxa.mongodb.net/?retryWrites=true&w=majority")
            db=client["Scrapper_db"]
            collec=db["scapper_table"]
            collec.insert_many(reviews)

            return render_template('result.html', reviews=reviews[0:(len(reviews)-1)])


        except Exception as e:
            print(e)
    else:
        return render_template('index.html')

if __name__=='__main__':
    app.run(host='0.0.0.0')



