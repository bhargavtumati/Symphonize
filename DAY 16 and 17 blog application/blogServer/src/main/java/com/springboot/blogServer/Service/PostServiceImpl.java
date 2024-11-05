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

	@Override
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

	@Override
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

	@Override
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

	@Override
	public List<Post> searchByName(String name){
		return postRepository.findAllByNameContaining(name);

	}

	@Override
	public Post editPost(Long id, Post post) {
	    Optional<Post> optionalPost = postRepository.findById(id);
	    if (optionalPost.isPresent()) {
	        Post existingPost = optionalPost.get();
	        existingPost.setName(post.getName());
	        existingPost.setContent(post.getContent());
	        existingPost.setImg(post.getImg());
	        existingPost.setTags(post.getTags());
	        existingPost.setViewCount(0);
	        existingPost.setLikeCount(0);
	        existingPost.setDate(new Date());
	        return postRepository.save(existingPost);
	    } else {
	        throw new EntityNotFoundException("Post Not Found");
	    }
	}

	@Override
	public String deletePost(Long id){
		Optional<Post> optionalPost = postRepository.findById(id);
		if (optionalPost.isPresent()) {
			Post post = optionalPost.get();

			postRepository.delete(post);
			return "Post got deleted";

		}
		else {
			throw new EntityNotFoundException("Post Not Found");
		}

	}


}
