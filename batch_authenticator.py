"""
Batch IC Authenticator - Process multiple images at once
"""

import os
import sys
import cv2
import json
from pathlib import Path
from smart_ic_authenticator import SmartICAuthenticator
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def process_batch(input_folder, output_json=None, save_debug_images=False):
    """Process all images in a folder"""
    authenticator = SmartICAuthenticator()
    
    # Supported image extensions
    extensions = ['*.png', '*.jpg', '*.jpeg', '*.bmp']
    
    # Find all images
    image_files = []
    for ext in extensions:
        image_files.extend(Path(input_folder).glob(ext))
    
    if not image_files:
        logger.error(f"No images found in {input_folder}")
        return
    
    logger.info(f"Found {len(image_files)} images to process")
    
    results = []
    
    for idx, img_path in enumerate(image_files, 1):
        logger.info(f"\n{'='*70}")
        logger.info(f"Processing {idx}/{len(image_files)}: {img_path.name}")
        logger.info(f"{'='*70}")
        
        try:
            result = authenticator.authenticate(str(img_path))
            result['filename'] = img_path.name
            result['filepath'] = str(img_path)
            results.append(result)
            
            # Save debug image if requested
            if save_debug_images and result.get('success'):
                debug_path = authenticator.save_debug_image(result)
                if debug_path:
                    logger.info(f"  Debug image saved: {debug_path}")
                
        except Exception as e:
            logger.error(f"Error processing {img_path.name}: {e}")
            results.append({
                'filename': img_path.name,
                'filepath': str(img_path),
                'error': str(e),
                'success': False
            })
    
    # Print summary
    print_summary(results)
    
    # Save results to JSON if requested
    if output_json:
        with open(output_json, 'w') as f:
            json.dump(results, f, indent=2)
        logger.info(f"\nResults saved to {output_json}")
    
    return results


def print_summary(results):
    """Print summary of batch processing"""
    print(f"\n{'='*70}")
    print("BATCH PROCESSING SUMMARY")
    print(f"{'='*70}")
    
    total = len(results)
    successful = sum(1 for r in results if r.get('success', False))
    authentic = sum(1 for r in results if r.get('verdict') == 'AUTHENTIC')
    likely_authentic = sum(1 for r in results if r.get('verdict') == 'LIKELY AUTHENTIC')
    suspicious = sum(1 for r in results if r.get('verdict') == 'SUSPICIOUS')
    counterfeit = sum(1 for r in results if r.get('verdict') == 'LIKELY COUNTERFEIT')
    
    print(f"Total Images: {total}")
    print(f"Successfully Processed: {successful}")
    print(f"Authentic: {authentic}")
    print(f"Likely Authentic: {likely_authentic}")
    print(f"Suspicious: {suspicious}")
    print(f"Likely Counterfeit: {counterfeit}")
    print(f"Errors: {total - successful}")
    
    # List any flagged chips
    flagged = [r for r in results if r.get('counterfeit_flags')]
    if flagged:
        print(f"\n⚠️  Chips with Counterfeit Indicators ({len(flagged)}):")
        for r in flagged:
            print(f"  - {r['filename']}: {len(r['counterfeit_flags'])} flags")
            for flag in r['counterfeit_flags']:
                print(f"      * {flag}")
    
    print(f"{'='*70}\n")


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python batch_authenticator.py <input_folder> [output.json] [--debug]")
        print("  --debug: Save debug images with bounding boxes")
        sys.exit(1)
    
    input_folder = sys.argv[1]
    output_json = sys.argv[2] if len(sys.argv) > 2 and not sys.argv[2].startswith('--') else None
    save_debug = '--debug' in sys.argv
    
    process_batch(input_folder, output_json, save_debug)
