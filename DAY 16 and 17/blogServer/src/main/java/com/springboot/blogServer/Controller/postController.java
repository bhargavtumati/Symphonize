package com.springboot.blogServer.Controller;

import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.DeleteMapping;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.PutMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import com.springboot.blogServer.Entity.Post;
import com.springboot.blogServer.Service.PostService;
import jakarta.persistence.EntityNotFoundException;


@RestController
@RequestMapping("/bhargavblog")
public class postController {

    private final PostService postService;

    public postController(PostService postService) {
        this.postService = postService;
    }

    @PostMapping("/CreatePost")
    public ResponseEntity<?> createPost(@RequestBody Post post) {
        try {
            Post createdPost = postService.savePost(post);
            return ResponseEntity.status(HttpStatus.CREATED).body(createdPost);
        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).build();
        }
    }

    @GetMapping("/getAllPosts")
    public ResponseEntity<?> getAllPosts() {
        try {
            return ResponseEntity.status(HttpStatus.OK).body(postService.getAllPosts());
        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).build();
        }
    }

    @GetMapping("/getPostById/{postId}")
    public ResponseEntity<?> getPostById(@PathVariable Long postId) {
        try {
            Post post = postService.getPostById(postId);
            return ResponseEntity.ok(post);
        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.NOT_FOUND).body(e.getMessage());
        }
    }

    @PutMapping("/LikePost/{postId}")
    public ResponseEntity<?> likePost(@PathVariable Long postId) {
        try {
            postService.LikePost(postId);
            return ResponseEntity.ok(new String[]{"Post Liked Successfully."});
        } catch (EntityNotFoundException e) {
            return ResponseEntity.status(HttpStatus.NOT_FOUND).body(e.getMessage());
        }
    }

    @GetMapping("/search/{name}")
    public ResponseEntity<?> searchByName(@PathVariable String name) {
        try {
            return ResponseEntity.status(HttpStatus.OK).body(postService.searchByName(name));
        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).build();
        }
    }

    @PutMapping("/edit/{postId}")
    public ResponseEntity<?> editPost(@PathVariable Long postId, @RequestBody Post post) {
        try {
            return ResponseEntity.status(HttpStatus.OK).body(postService.editPost(postId, post));
        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).build();
        }
    }

    @DeleteMapping("/delete/{postId}")
    public ResponseEntity<?> deletePost(@PathVariable Long postId) {
        try {
            return ResponseEntity.status(HttpStatus.OK).body(postService.deletePost(postId));
        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).build();
        }
    }
}
