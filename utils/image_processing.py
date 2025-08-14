"""
Image processing utilities for OPPO A92 optimization
"""
import cv2
import numpy as np
from typing import Tuple, List, Optional

def resize_for_mobile(image, max_width=640, max_height=480):
    """
    Resize image for mobile processing while maintaining aspect ratio
    
    Args:
        image: Input image
        max_width: Maximum width
        max_height: Maximum height
        
    Returns:
        Resized image and scale factor
    """
    height, width = image.shape[:2]
    
    # Calculate scaling factor
    scale_w = max_width / width
    scale_h = max_height / height
    scale = min(scale_w, scale_h)
    
    if scale >= 1.0:
        return image, 1.0
    
    # Resize image
    new_width = int(width * scale)
    new_height = int(height * scale)
    
    resized = cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_AREA)
    return resized, scale

def enhance_for_detection(image):
    """
    Enhance image for better AI detection on OPPO A92
    
    Args:
        image: Input image
        
    Returns:
        Enhanced image
    """
    # Convert to LAB color space for better contrast
    lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    
    # Apply CLAHE to L channel
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    l = clahe.apply(l)
    
    # Merge channels and convert back to BGR
    enhanced = cv2.merge([l, a, b])
    enhanced = cv2.cvtColor(enhanced, cv2.COLOR_LAB2BGR)
    
    return enhanced

def reduce_noise(image):
    """
    Reduce noise for better processing
    
    Args:
        image: Input image
        
    Returns:
        Denoised image
    """
    # Use bilateral filter to reduce noise while preserving edges
    denoised = cv2.bilateralFilter(image, 9, 75, 75)
    return denoised

def optimize_brightness_contrast(image, alpha=1.1, beta=10):
    """
    Optimize brightness and contrast for OPPO A92
    
    Args:
        image: Input image
        alpha: Contrast factor (1.0-2.0)
        beta: Brightness offset (-100 to 100)
        
    Returns:
        Optimized image
    """
    # Apply linear transformation: new_image = alpha * image + beta
    optimized = cv2.convertScaleAbs(image, alpha=alpha, beta=beta)
    return optimized

def crop_roi(image, bbox, padding=0.1):
    """
    Crop region of interest with padding
    
    Args:
        image: Input image
        bbox: Bounding box [x1, y1, x2, y2]
        padding: Padding factor (0.0-1.0)
        
    Returns:
        Cropped image region
    """
    height, width = image.shape[:2]
    x1, y1, x2, y2 = bbox
    
    # Calculate padding
    w = x2 - x1
    h = y2 - y1
    pad_w = int(w * padding)
    pad_h = int(h * padding)
    
    # Apply padding with bounds checking
    x1 = max(0, x1 - pad_w)
    y1 = max(0, y1 - pad_h)
    x2 = min(width, x2 + pad_w)
    y2 = min(height, y2 + pad_h)
    
    return image[y1:y2, x1:x2]

def create_detection_overlay(image, detections, class_colors=None):
    """
    Create overlay with detection results
    
    Args:
        image: Base image
        detections: List of detection results
        class_colors: Color mapping for classes
        
    Returns:
        Image with overlay
    """
    overlay = image.copy()
    
    if class_colors is None:
        class_colors = {
            'car': (0, 255, 0),
            'motorcycle': (255, 0, 0),
            'bus': (0, 255, 255),
            'truck': (255, 0, 255)
        }
    
    for detection in detections:
        bbox = detection.get('bbox', [])
        if len(bbox) != 4:
            continue
            
        x1, y1, x2, y2 = bbox
        vehicle_class = detection.get('class', 'unknown')
        confidence = detection.get('confidence', 0)
        license_plate = detection.get('license_plate', '')
        
        # Get color for vehicle class
        color = class_colors.get(vehicle_class, (255, 255, 255))
        
        # Draw bounding box
        cv2.rectangle(overlay, (x1, y1), (x2, y2), color, 2)
        
        # Draw labels
        labels = []
        labels.append(f"{vehicle_class}: {confidence:.2f}")
        
        if license_plate:
            labels.append(f"Plate: {license_plate}")
        
        # Draw label background
        label_text = " | ".join(labels)
        label_size = cv2.getTextSize(label_text, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2)[0]
        
        cv2.rectangle(overlay, (x1, y1 - label_size[1] - 10), 
                     (x1 + label_size[0], y1), color, -1)
        
        # Draw label text
        cv2.putText(overlay, label_text, (x1, y1 - 5), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
    
    return overlay

def save_detection_image(image, detections, filename, include_overlay=True):
    """
    Save detection image with optional overlay
    
    Args:
        image: Original image
        detections: Detection results
        filename: Output filename
        include_overlay: Whether to include detection overlay
        
    Returns:
        Success status
    """
    try:
        if include_overlay and detections:
            save_image = create_detection_overlay(image, detections)
        else:
            save_image = image
        
        return cv2.imwrite(filename, save_image)
        
    except Exception as e:
        print(f"❌ Error saving detection image: {e}")
        return False

def calculate_image_quality_score(image):
    """
    Calculate image quality score for processing
    
    Args:
        image: Input image
        
    Returns:
        Quality score (0.0-1.0)
    """
    try:
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Calculate sharpness using Laplacian variance
        laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
        
        # Normalize sharpness score (higher is better)
        sharpness_score = min(1.0, laplacian_var / 1000.0)
        
        # Calculate brightness score
        brightness = np.mean(gray)
        brightness_score = 1.0 - abs(brightness - 128) / 128.0  # Optimal at 128
        
        # Calculate contrast score
        contrast = np.std(gray)
        contrast_score = min(1.0, contrast / 64.0)
        
        # Combined quality score
        quality_score = (sharpness_score * 0.5 + brightness_score * 0.3 + contrast_score * 0.2)
        
        return quality_score
        
    except Exception as e:
        print(f"❌ Error calculating image quality: {e}")
        return 0.5  # Default medium quality

def memory_efficient_processing(image, processing_func, chunk_size=None):
    """
    Process image in chunks for memory efficiency on OPPO A92
    
    Args:
        image: Input image
        processing_func: Function to apply to image chunks
        chunk_size: Size of chunks to process
        
    Returns:
        Processed image
    """
    height, width = image.shape[:2]
    
    # Default chunk size based on image size
    if chunk_size is None:
        chunk_size = min(256, height // 4, width // 4)
    
    # If image is small enough, process normally
    if height <= chunk_size and width <= chunk_size:
        return processing_func(image)
    
    # Process in overlapping chunks
    processed = np.zeros_like(image)
    overlap = chunk_size // 4
    
    for y in range(0, height, chunk_size - overlap):
        for x in range(0, width, chunk_size - overlap):
            # Define chunk boundaries
            y1 = y
            y2 = min(y + chunk_size, height)
            x1 = x
            x2 = min(x + chunk_size, width)
            
            # Extract and process chunk
            chunk = image[y1:y2, x1:x2]
            processed_chunk = processing_func(chunk)
            
            # Blend chunk back (simple averaging for overlap)
            if y == 0 and x == 0:
                processed[y1:y2, x1:x2] = processed_chunk
            else:
                # Weighted blending for overlapping regions
                processed[y1:y2, x1:x2] = cv2.addWeighted(
                    processed[y1:y2, x1:x2], 0.5,
                    processed_chunk, 0.5, 0
                )
    
    return processed

def adaptive_threshold_for_plates(image):
    """
    Apply adaptive thresholding optimized for license plates
    
    Args:
        image: Grayscale image
        
    Returns:
        Thresholded image
    """
    # Apply Gaussian adaptive threshold
    thresh = cv2.adaptiveThreshold(
        image, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY, 11, 2
    )
    
    return thresh

def morphological_cleanup(image, operation='close', kernel_size=3):
    """
    Apply morphological operations for image cleanup
    
    Args:
        image: Binary image
        operation: Morphological operation ('open', 'close', 'gradient')
        kernel_size: Size of morphological kernel
        
    Returns:
        Cleaned image
    """
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (kernel_size, kernel_size))
    
    if operation == 'open':
        result = cv2.morphologyEx(image, cv2.MORPH_OPEN, kernel)
    elif operation == 'close':
        result = cv2.morphologyEx(image, cv2.MORPH_CLOSE, kernel)
    elif operation == 'gradient':
        result = cv2.morphologyEx(image, cv2.MORPH_GRADIENT, kernel)
    else:
        result = image
    
    return result