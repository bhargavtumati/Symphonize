'use client'

import React from 'react';
import { useUpload } from './uploadContext';
import ProgressModal from './progressModel';

const GlobalUploadStatus: React.FC = () => {
  const { files, setFiles, isMinimized, setIsMinimized, showProgressModal, setShowProgressModal } = useUpload();

  const handleMaximize = () => {
    setIsMinimized(false);
    setShowProgressModal(true);
  };

  const handleMinimize = () => {
    setIsMinimized(true);
    setShowProgressModal(false);
  };

  const handleClose = () => {
    setShowProgressModal(false);
    setIsMinimized(false);
    setFiles([]);
    window.location.reload();
  };


  if (!isMinimized && !showProgressModal) {
    return null;
  }

  return (
    <ProgressModal
      initialFiles={files}
      onClose={handleClose}
      onMinimize={handleMinimize}
      isMinimized={isMinimized}
      onMaximize={handleMaximize}
    />
  );
};

export default GlobalUploadStatus;

