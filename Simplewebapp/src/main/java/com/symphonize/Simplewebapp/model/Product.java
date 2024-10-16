package com.symphonize.Simplewebapp.model;


public class Product {
     
	
	private int prodId;
     private String prodName;
     private int price;
    
     
     
     public Product(int i, String Product, int j) {
 		// TODO Auto-generated constructor stub
    	 
     	 this.prodId=i;
     	 this.prodName=Product;
     	 this.price=j;
     	 
 	}
     
     
	@Override
	public String toString() {
		// TODO Auto-generated method stub
		return super.toString();
	}


	public int getProdId() {
		return prodId;
	}
	public void setProdId(int prodId) {
		this.prodId = prodId;
	}
	public String getProdName() {
		return prodName;
	}
	public void setProdName(String prodName) {
		this.prodName = prodName;
	}
	public int getPrice() {
		return price;
	}
	public void setPrice(int price) {
		this.price = price;
	}
	
     
	
     
     
}
