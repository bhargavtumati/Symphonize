package com.symphonize.Simplewebapp.service;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;

import org.springframework.stereotype.Component;

import com.symphonize.Simplewebapp.model.Product;

@Component
public class ProductService {
   
	List<Product> products =new ArrayList<>(Arrays.asList(new Product(101,"Iphone",50000),new Product(102,"Samsung",60000)));
	
	public List<Product> getProducts(){
		return products;
	}
	
	public Product getProductById(int prodId) {
		// TODO Auto-generated method stub
		return products.stream().filter(p->p.getProdId()==prodId).findFirst().orElse(new Product(prodId,"No Item", 0));
	}

	public void addProduct(Product prod) {
		// TODO Auto-generated method stub
		products.add(prod);
		
	}
	
	



	
}
