package com.springboot.blogServer.Controller;


import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import com.springboot.blogServer.Entity.Post;
import com.springboot.blogServer.Server.PostService;



@RestController
@RequestMapping("/api/posts")
public class postController {

	
	
	private PostService postservice;
	
	public postController(PostService postservice) {
		super();
		this.postservice = postservice;
	}
	
	@PostMapping
	public ResponseEntity<?> createPost(@RequestBody Post post){
		try {
			Post createdPost = postservice.savePost(post);
			return ResponseEntity.status(HttpStatus.CREATED).body(createdPost);
		}
		catch(Exception e) {
			return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).build();
		}
	}
	
	@GetMapping
	public ResponseEntity<?> getAllPosts(){
		try {
			return ResponseEntity.status(HttpStatus.OK).body(postservice.getAllPosts());
		}
		catch(Exception e) {
			return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).build();
		}
	}
	
	@GetMapping("{postId}")
	public ResponseEntity<?> getPostById(@PathVariable Long postId){
		try {
			Post post = postservice.getPostById(postId);
			return ResponseEntity.ok(post);
			
		}
		catch(Exception e) {
			return ResponseEntity.status(HttpStatus.NOT_FOUND).body(e.getMessage());
		}
	}
	
	@Putmapping("{postId}")
	public ResponseEntity<?> getPostById(@PathVariable Long postId){
		
	}
	
	
}
