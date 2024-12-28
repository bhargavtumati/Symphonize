package com.springboot.blogServer.Service;

import java.util.List;

import com.springboot.blogServer.Entity.Comment;

public interface CommentService {

	 Comment createComment(Long postid, String postBy, String content);

	 List<Comment> getCommentsByPostId(Long postId);




}
