# Watermarker Pro

A desktop application for adding text and image watermarks to photos automatically. Built with Python, Tkinter, and Pillow.

## Overview

Instead of manually adding watermarks in Photoshop or other expensive image editing software, Watermarker Pro lets you batch-process multiple images with custom watermarks. Perfect for photographers, content creators, and anyone who needs to add logos or branding to images at scale.

**Use Case:** You're posting photos to Instagram but want to add your website/logo to all of them automatically. Just configure your watermark once and process all images at once.

## Features

### Watermark Types
- **Text Watermarks** - Add custom text with adjustable:
  - Font selection (system fonts or custom TTF/OTF)
  - Color picker
  - Text alignment (Left, Center, Right)
  - Multi-line support (Enter for new line, Shift+Enter to preview)
  
- **Image Watermarks** - Add logo/PNG images with:
  - Image file selection
  - Scaling control
  - Transparency adjustment

### Positioning & Customization
- **9-Point Grid System** - Place watermarks in:
  - Top-Left, Top-Center, Top-Right
  - Center-Left, Center, Center-Right
  - Bottom-Left, Bottom-Center, Bottom-Right
  
- **Fine Controls**
  - Size: 0-100%
  - Transparency: 0-100%
  - Edge Padding: 0-100px

### Batch Processing
- Upload multiple images at once
- Preview watermark in real-time on canvas
- Process entire batch with progress indicator
- Error handling with skip/abort options
- Automatic filename collision detection
- Saves as: `filename_watermarked.jpg`

### Preview & Responsiveness
- Live canvas preview updates as you adjust settings
- Smooth window resizing with maintained preview
- Threading ensures UI stays responsive during batch processing
- Keyboard shortcuts: Shift+Enter to trigger preview

## Installation

### Requirements
- Python 3.8+
- Pillow 7.0+ (for image processing)
- Tkinter (usually comes with Python)

### Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/watermarker-pro.git
   cd watermarker-pro
   ```

2. **Install dependencies**
   ```bash
   pip install Pillow
   ```

3. **Run the application**
   ```bash
   python main.py
   ```

## Usage

### Adding a Text Watermark

1. **Select Text mode** (default)
2. **Enter your text** in the text box (supports multi-line)
3. **Choose a font** - Select from system fonts or click "Add Font..." for custom TTF/OTF
4. **Pick a color** - Click "Choose a colour" button
5. **Adjust alignment** - Left, Center, or Right
6. **Configure position** - Choose from 9 grid positions (Bottom-Right is default)
7. **Fine-tune size and transparency** - Use sliders to preview
8. **Upload images** - Click "Upload Image(s)" to select photos
9. **Process** - Click "Start", select save folder, wait for completion

### Adding an Image Watermark

1. **Select Image mode** - Toggle the radio button
2. **Select watermark file** - Click "Select Watermark File" (PNG/JPG)
3. **Configure position** - Choose grid position
4. **Adjust size & transparency** - Use sliders
5. **Upload images** and **Process** - Same as text watermarks

## Project Structure

```
watermarker-pro/
├── main.py              # Application orchestrator, threading, preview updates
├── image_engine.py      # Pillow backend, image processing operations
├── ui_layout.py         # Tkinter GUI, widgets, layout management
└── README.md            # Documentation
```

### Architecture

- **MVC-inspired design** - Separation of concerns:
  - **main.py** = Controller (orchestration)
  - **ui_layout.py** = View (GUI)
  - **image_engine.py** = Model (data & processing)

- **Threading** - Batch processing runs on separate thread to keep UI responsive
- **State Management** - UI state collected in dictionary, passed to engine
- **Error Handling** - Try/catch with user-friendly error dialogs

## Technical Details

### Image Processing
- Uses Pillow (PIL) for all image operations
- Converts to RGBA for watermark compositing
- Saves final output as RGB (JPG-compatible)
- Supports: PNG, JPG, JPEG input formats

### Text Rendering
- Multiline text support with proper line measurement
- Font fallback system for cross-platform compatibility
- Alpha channel manipulation for transparency
- Text bounding box calculation and positioning

### Performance
- Image watermark cached in memory after first load
- Live preview downsampled to canvas size
- Threading prevents UI blocking during batch processing
- Minimal memory footprint with proper resource cleanup

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| Shift+Enter | Trigger preview update |
| Click away from text box | Trigger preview update |
| Release mouse on slider | Trigger preview update |

## Troubleshooting

### Preview doesn't show watermark
- Ensure you've uploaded at least one image
- Try clicking "Preview" button or Shift+Enter
- Check console for error messages

### Batch processing fails on some images
- Click "Skip" to continue with remaining images
- Check file format (supported: PNG, JPG, JPEG)
- Ensure save folder has write permissions
- Check if image files are corrupted

### Text appears tiny/huge
- Adjust the **Size (%)** slider
- Try different font sizes
- Text scales relative to image height

### Font selection doesn't work
- Ensure TTF/OTF file is valid
- Some system fonts may not be available on all platforms
- Use "DejaVuSans.ttf" as fallback (usually included)

## Known Limitations

- Watermark does not support rotation
- Text shadows/outlines not supported (only solid color)
- Limited to single watermark per image (not layered)
- Preview canvas maximum ~800x720px

## Future Enhancements

- Watermark rotation support
- Multiple watermarks per image
- Text shadow/outline effects
- Pattern/gradient watermarks
- Batch template presets
- Export settings for reuse

## Dependencies

| Library | Version | Purpose |
|---------|---------|---------|
| Pillow | 7.0+ | Image processing, font rendering |
| Tkinter | builtin | GUI framework |

## Similar Tools

- [Watermarkly](https://watermarkly.com/) - Online watermarking service
- [ImageMagick](https://imagemagick.org/) - Command-line image processing
- Adobe Photoshop - Professional (paid)

## License

MIT License - Feel free to use, modify, and distribute

## Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/your-feature`)
3. Commit changes (`git commit -m 'Add feature'`)
4. Push to branch (`git push origin feature/your-feature`)
5. Open a Pull Request

## Support

Found a bug? Have a feature request? 
- Open an [issue](https://github.com/Joshuaongith/image_watermarking_project/issues)
- Include Python version, OS, and steps to reproduce
- Attach example image if relevant

## Author

Created as a practical Tkinter + Pillow project

## Changelog

### v1.0.0 (Initial Release)
- Text and image watermark support
- 9-point grid positioning system
- Real-time preview
- Batch processing with threading
- Error handling and recovery
- Custom font support
- Color picker for text watermarks

## Roadmap

Future development focuses on expanding accessibility so users will not need to use the terminal. Pre-compiled, standalone graphical executables are planned for release in the following order:
1. **Linux** (AppImage / Native Binary)
2. **Windows** (.exe)
3. **macOS** (.dmg / .app)

## Licence

This project is licensed under the **GNU General Public License v3.0 (GPLv3)**. 

This is a strong copyleft licence. It means that anyone is free to use, modify, and distribute this software, but **any derivative works, modifications, or compiled versions must also be released as open-source software under the exact same GPLv3 terms**. You cannot take this code, modify it, and distribute it as closed-source or proprietary software. 

See the `LICENSE` file for the complete legal text.
---

**Happy watermarking! 📸**