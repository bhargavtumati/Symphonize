package com.springboot.blogServer.Service;

import java.util.Date;
import java.util.List;
import java.util.Optional;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import com.springboot.blogServer.Entity.Comment;
import com.springboot.blogServer.Entity.Post;
import com.springboot.blogServer.Repo.CommentRepository;
import com.springboot.blogServer.Repo.PostRepository;

import jakarta.persistence.EntityNotFoundException;

@Service
public class CommentServiceImpl implements CommentService {

	@Autowired
	private CommentRepository commentRepository;
	
	
	@Autowired
	private PostRepository postrepository;
	
	public Comment createComment(Long postid, String postBy, String content) {
		
		Optional<Post> optionalPost = postrepository.findById(postid);
		if(optionalPost.isPresent()) {
			Comment comment = new Comment();
			comment.setId(postid);
			comment.setPost(optionalPost.get());
			comment.setContent(content);
			comment.setPostedBy(postBy);
			comment.setCreatedAt(new Date());
			
			return commentRepository.save(comment);
		}
		else {
			throw new EntityNotFoundException("Post not found");
		}
		
		
	}
	
	public List<Comment> getCommentsByPostId(Long postId){
		return commentRepository.findByPostId(postId);
	}
}
