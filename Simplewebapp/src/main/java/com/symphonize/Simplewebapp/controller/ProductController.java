package com.symphonize.Simplewebapp.controller;

import java.util.List;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RestController;

import com.symphonize.Simplewebapp.model.Product;
import com.symphonize.Simplewebapp.service.ProductService;

@RestController
public class ProductController {
    @Autowired
	ProductService service;
    
    @GetMapping("/products")
	public List<Product> getProducts() {
		return service.getProducts();
	}
    @GetMapping("/products/{prodId}")
    public Product getproductById(@PathVariable int prodId) {
    	return service.getProductById(prodId);
    }
    @PostMapping("/products")
    public void addProduct(@RequestBody Product prod) {
    	service.addProduct(prod);
    }
}
