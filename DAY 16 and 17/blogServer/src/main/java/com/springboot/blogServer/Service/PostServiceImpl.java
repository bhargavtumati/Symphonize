package com.springboot.blogServer.Service;

import java.util.Date;
import java.util.List;
import java.util.Optional;

import org.springframework.stereotype.Service;

import com.springboot.blogServer.Entity.Post;
import com.springboot.blogServer.Repo.PostRepository;

import jakarta.persistence.EntityNotFoundException;


@Service
public class PostServiceImpl implements PostService {
		
	private PostRepository postRepository;
	
	public PostServiceImpl(PostRepository postRepository) {
		super();
		this.postRepository = postRepository;
	}

	public Post savePost(Post post) {
		post.setViewCount(0);
		post.setLikeCount(0);
		post.setDate(new Date());
		
		return postRepository.save(post);
		
	}

	@Override
	public List<Post> getAllPosts() {
		
		return postRepository.findAll();
	}
	
	public Post getPostById(Long id) {
		
		Optional<Post> optionalPost = postRepository.findById(id);
		
		if (optionalPost.isPresent()) {
			Post post = optionalPost.get();
			post.setViewCount(post.getViewCount()+1);
			return postRepository.save(post);
			
		}
		else {
			throw new EntityNotFoundException("Post Not Found");
		}
		
		
	}
	
	public void LikePost(Long id) {
		Optional<Post> optionalPost = postRepository.findById(id);
		
		if (optionalPost.isPresent()) {
			Post post = optionalPost.get();
			post.setLikeCount(post.getLikeCount()+1);
			postRepository.save(post);
			
		}
		else {
			throw new EntityNotFoundException("Post Not Found with id: "+id );
		}
	}
	
	public List<Post> searchByName(String name){
		return postRepository.findAllByNameContaining(name);
		
	}

}
