package com.springboot.VirtualBookStrore.Repo;

import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import com.springboot.VirtualBookStrore.Entity.Library;

@Repository
public interface LibraryRepo extends JpaRepository<Library, Long> {
    Page<Library> findAll(Pageable pageable);
}
