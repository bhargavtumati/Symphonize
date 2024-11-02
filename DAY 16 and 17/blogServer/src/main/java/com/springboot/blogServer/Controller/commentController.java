package com.springboot.blogServer.Controller;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.CrossOrigin;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import com.springboot.blogServer.Service.CommentService;

@RestController
@RequestMapping("/bhargavBlog/")
@CrossOrigin
public class commentController {
	
	@Autowired
	private CommentService commentservice;
	
	@PostMapping("/comment/create")
	public ResponseEntity<?> createComment(@RequestParam Long postId, @RequestParam String postedBy, @RequestBody String content){
		
		try {
			return ResponseEntity.ok(commentservice.createComment(postId, postedBy, content));
		}
		catch(Exception e) {
			return ResponseEntity.status(HttpStatus.NOT_ACCEPTABLE).body(e.getMessage());
		}
		
	}
	
	@GetMapping("/getAllCommentsBy/{PostId}")
	public ResponseEntity<?> getcommentsByPostId(@PathVariable Long PostId){
		try {
			return ResponseEntity.ok(commentservice.getCommentsByPostId(PostId));
		}
		catch(Exception e){
			
			return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body("Something went wrong");
			
		}
	}

}
