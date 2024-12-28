import React, { useEffect, useState } from 'react';

const CustomizationForm = () => {
  // State for form fields
  const [enableCoverPhoto, setEnableCoverPhoto] = useState(false);
  const [heading, setHeading] = useState('Welcome to Career Page');
  const [description, setDescription] = useState('Here you can explore opportunities.');
  const [darkMode, setDarkMode] = useState(false);
  const [colorSelected, setColorSelected] = useState('blue');
  const [fontSelected, setFontSelected] = useState('Times New Roman');
  const [coverPhoto, setCoverPhoto] = useState(null);

  // State for dynamic data (colors and fonts)
  const [colors, setColors] = useState([]);
  const [fonts, setFonts] = useState([]);
  const [recentColors, setRecentColors] = useState([]); // Recently used colors

  // Fetch colors and fonts from JSON files
  useEffect(() => {
    fetch('/colors.json')
      .then(response => response.json())
      .then(data => setColors(data.colors))
      .catch(error => console.error('Error fetching colors:', error));

    fetch('/fonts.json')
      .then(response => response.json())
      .then(data => setFonts(data.fonts))
      .catch(error => console.error('Error fetching fonts:', error));
  }, []);

  // Handle the cover photo upload
  const handleCoverPhotoChange = (e) => {
    setCoverPhoto(e.target.files[0]);
  };

  // Handle form submission
  const handleSubmit = (e) => {
    e.preventDefault();

    // Prepare form data to send to the backend
    const formData = new FormData();
    formData.append('enable_cover_photo', enableCoverPhoto);
    formData.append('heading', heading);
    formData.append('description', description);
    formData.append('dark_mode', darkMode);
    formData.append('color_selected', colorSelected);
    formData.append('font', fontSelected);

    if (coverPhoto) {
      formData.append('file', coverPhoto);
    }

    // Send the data to the backend API
    fetch('/customizations/your-domain', {
      method: 'POST',
      body: formData,
    })
      .then((response) => response.json())
      .then((data) => {
        alert('Settings saved successfully!');
      })
      .catch((error) => {
        console.error('Error saving settings:', error);
        alert('Failed to save settings.');
      });
  };

  // Handle adding a recently used color
  const handleColorSelect = (color) => {
    setColorSelected(color);
    // Add to recently used colors if not already in the list
    if (!recentColors.includes(color)) {
      setRecentColors([color, ...recentColors].slice(0, 10)); // Keep only the last 10
    }
  };

  // Handle new color button click (optional integration with color picker)
  const handleNewColor = () => {
    alert('Open color picker here!');
    // Replace this with actual color picker logic (e.g., using react-color)
  };

  return (
    <div className="customization-form">
      <h1>Customize Your Career Page</h1>
      <form onSubmit={handleSubmit}>
        <div className="setting">
          <label>
            Enable Cover Photo:
            <input
              type="checkbox"
              checked={enableCoverPhoto}
              onChange={() => setEnableCoverPhoto(!enableCoverPhoto)}
            />
          </label>
        </div>

        {enableCoverPhoto && (
          <div className="setting">
            <label>
              Upload Cover Photo:
              <input
                type="file"
                accept="image/*"
                onChange={handleCoverPhotoChange}
              />
            </label>
          </div>
        )}

        <div className="setting">
          <label>
            Heading:
            <input
              type="text"
              value={heading}
              onChange={(e) => setHeading(e.target.value)}
              placeholder="Enter heading"
            />
          </label>
        </div>

        <div className="setting">
          <label>
            Description:
            <textarea
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Enter description"
            />
          </label>
        </div>

        <div className="setting">
          <label>
            Enable Dark Mode:
            <input
              type="checkbox"
              checked={darkMode}
              onChange={() => setDarkMode(!darkMode)}
            />
          </label>
        </div>

        {/* Color Selection */}
        <div className="setting">
          <label>
            Select a Color:
            <select
              value={colorSelected}
              onChange={(e) => handleColorSelect(e.target.value)}
            >
              {colors.map((color) => (
                <option key={color.hex_code} value={color.hex_code}>
                  {color.name}
                </option>
              ))}
            </select>
          </label>
        </div>

        <div className="setting">
          <button type="button" onClick={handleNewColor}>
            New Color
          </button>
        </div>

        {/* Recently Used Colors */}
        <div className="setting">
          <h4>Recently Used Colors:</h4>
          <div style={{ display: 'flex', flexWrap: 'wrap' }}>
            {recentColors.map((color, index) => (
              <div
                key={index}
                onClick={() => handleColorSelect(color)}
                style={{
                  width: '40px',
                  height: '40px',
                  margin: '5px',
                  backgroundColor: color,
                  cursor: 'pointer',
                  borderRadius: '5px',
                }}
              />
            ))}
          </div>
        </div>

        {/* Font Selection */}
        <div className="setting">
          <label>
            Select Font Style:
            <select
              value={fontSelected}
              onChange={(e) => setFontSelected(e.target.value)}
            >
              {fonts.map((font) => (
                <option key={font.name} value={font.name}>
                  {font.name}
                </option>
              ))}
            </select>
          </label>
        </div>

        <div className="setting">
          <button type="submit">Save Settings</button>
        </div>

        <div className="setting">
          <button type="submit">Cancel Settings</button>
        </div>
      </form>
    </div>
  );
};

export default CustomizationForm;
