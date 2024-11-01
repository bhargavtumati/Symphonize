package com.springboot.blogServer.Server;


import java.util.List;

import com.springboot.blogServer.Entity.Post;


public interface PostService {

	Post savePost(Post post);
	
	List<Post> getAllPosts();
	
	Post getPostById(Long id);
	
	void LikePost(Long id) ;
}
