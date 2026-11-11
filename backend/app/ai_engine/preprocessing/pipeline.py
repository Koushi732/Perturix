import logging
import time

from . import core
from .config import PreprocessingConfig
from .models import PreprocessingOutput

logger = logging.getLogger(__name__)

def run_preprocessing_pipeline(filepath: str, config: PreprocessingConfig | None = None) -> PreprocessingOutput:
    """Executes the full preprocessing pipeline on a given image file."""
    start_time = time.perf_counter()
    if config is None:
        config = PreprocessingConfig()
        
    logger.info("Starting preprocessing pipeline")
    
    try:
        # Step 1: Load Image
        image = core.load_image(filepath)
        original_width, original_height = image.size
        
        # Step 2: Convert to RGB
        if config.to_rgb:
            image = core.convert_to_rgb(image)
            
        # Step 3: Resize (Optional)
        if config.target_size:
            image = core.resize_image(image, config.target_size)
            width, height = config.target_size
        else:
            width, height = original_width, original_height
            
        # Step 4: Convert to NumPy
        array = core.image_to_numpy(image)
        
        # Step 5: Convert to Tensor and reshape
        tensor = core.numpy_to_tensor(array)
        
        # Step 6: Normalize
        if config.normalize:
            tensor = core.normalize_tensor(tensor)
            
        # Step 7: Add Batch Dimension
        if config.add_batch_dimension:
            tensor = core.prepare_batch(tensor)
            
        # Extract metadata
        channels = tensor.shape[1] if config.add_batch_dimension else tensor.shape[0]
        
        processing_time_ms = (time.perf_counter() - start_time) * 1000
        logger.info(f"Preprocessing completed in {processing_time_ms:.2f}ms")
        
        return PreprocessingOutput(
            tensor=tensor,
            width=width,
            height=height,
            channels=channels,
            normalized=config.normalize,
            processing_time_ms=processing_time_ms
        )
        
    except Exception as e:
        logger.error(f"Error during preprocessing pipeline: {e!s}")
        raise
