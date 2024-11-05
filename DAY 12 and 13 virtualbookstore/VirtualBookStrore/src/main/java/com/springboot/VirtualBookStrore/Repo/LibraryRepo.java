package com.springboot.VirtualBookStrore.Repo;

import org.springframework.data.jpa.repository.JpaRepository;

import com.springboot.VirtualBookStrore.Entity.Library;



public interface LibraryRepo extends JpaRepository<Library, Long> {

}
