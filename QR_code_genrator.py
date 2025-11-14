import streamlit as st
import qrcode
from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.moduledrawers import RoundedModuleDrawer, CircleModuleDrawer, GappedSquareModuleDrawer, VerticalBarsDrawer, HorizontalBarsDrawer
from qrcode.image.styles.colormasks import SolidFillColorMask, SquareGradiantColorMask, RadialGradiantColorMask
from PIL import Image
import io

st.set_page_config(page_title="QR Code Art Generator", page_icon="🎨", layout="wide")

# Custom CSS
st.markdown("""
    <style>
    .main {
        padding: 2rem;
    }
    .stButton>button {
        width: 100%;
        background-color: #FF4B4B;
        color: white;
        font-weight: bold;
        border-radius: 10px;
        padding: 0.5rem;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🎨 QR Code Art Generator")
st.markdown("Create beautiful, artistic QR codes with custom styles and colors!")

# Sidebar for settings
with st.sidebar:
    st.header("⚙️ QR Code Settings")
    
    # URL/Text input
    data = st.text_area("Enter URL or Text:", placeholder="https://example.com", height=100)
    
    # Error correction level
    error_correction = st.selectbox(
        "Error Correction Level:",
        options=["Low (7%)", "Medium (15%)", "Quartile (25%)", "High (30%)"],
        index=1
    )
    
    error_map = {
        "Low (7%)": qrcode.constants.ERROR_CORRECT_L,
        "Medium (15%)": qrcode.constants.ERROR_CORRECT_M,
        "Quartile (25%)": qrcode.constants.ERROR_CORRECT_Q,
        "High (30%)": qrcode.constants.ERROR_CORRECT_H
    }
    
    # Size
    box_size = st.slider("QR Code Size:", 5, 20, 10)
    border = st.slider("Border Size:", 1, 10, 4)

# Main content area
col1, col2 = st.columns(2)

with col1:
    st.subheader("🎭 Style Options")
    
    # Module drawer style
    module_style = st.selectbox(
        "Module Style:",
        options=["Square", "Rounded", "Circle", "Gapped Square", "Vertical Bars", "Horizontal Bars"]
    )
    
    module_map = {
        "Square": None,
        "Rounded": RoundedModuleDrawer(),
        "Circle": CircleModuleDrawer(),
        "Gapped Square": GappedSquareModuleDrawer(),
        "Vertical Bars": VerticalBarsDrawer(),
        "Horizontal Bars": HorizontalBarsDrawer()
    }
    
    # Color style
    color_style = st.selectbox(
        "Color Style:",
        options=["Solid", "Square Gradient", "Radial Gradient"]
    )
    
    # Color pickers
    if color_style == "Solid":
        fill_color = st.color_picker("Fill Color:", "#000000")
        back_color = st.color_picker("Background Color:", "#FFFFFF")
    else:
        center_color = st.color_picker("Center Color:", "#FF0000")
        edge_color = st.color_picker("Edge Color:", "#0000FF")
        back_color = st.color_picker("Background Color:", "#FFFFFF")

with col2:
    st.subheader("🖼️ Logo Options")
    
    use_logo = st.checkbox("Add Logo/Image in Center")
    
    if use_logo:
        logo_file = st.file_uploader("Upload Logo:", type=["png", "jpg", "jpeg"])
        if logo_file:
            logo = Image.open(logo_file)
            st.image(logo, caption="Logo Preview", width=150)

# Generate button
if st.button("🎨 Generate QR Code", type="primary"):
    if not data:
        st.error("⚠️ Please enter URL or text!")
    else:
        try:
            # Create QR code
            qr = qrcode.QRCode(
                version=1,
                error_correction=error_map[error_correction],
                box_size=box_size,
                border=border,
            )
            qr.add_data(data)
            qr.make(fit=True)
            
            # Create color mask
            if color_style == "Solid":
                color_mask = SolidFillColorMask(
                    back_color=back_color,
                    front_color=fill_color
                )
            elif color_style == "Square Gradient":
                color_mask = SquareGradiantColorMask(
                    back_color=back_color,
                    center_color=center_color,
                    edge_color=edge_color
                )
            else:  # Radial Gradient
                color_mask = RadialGradiantColorMask(
                    back_color=back_color,
                    center_color=center_color,
                    edge_color=edge_color
                )
            
            # Generate image
            if module_style == "Square":
                img = qr.make_image(fill_color=fill_color if color_style == "Solid" else None, 
                                   back_color=back_color)
            else:
                img = qr.make_image(
                    image_factory=StyledPilImage,
                    module_drawer=module_map[module_style],
                    color_mask=color_mask
                )
            
            # Convert QR code to PIL Image if needed
            if not isinstance(img, Image.Image):
                img = img.convert('RGB')
            
            # Add logo if selected
            if use_logo and logo_file:
                logo = Image.open(logo_file).convert('RGBA')
                # Calculate logo size (about 1/5 of QR code)
                qr_width, qr_height = img.size
                logo_size = qr_width // 5
                logo = logo.resize((logo_size, logo_size), Image.Resampling.LANCZOS)
                
                # Create a white background for the logo area
                logo_bg = Image.new('RGB', (logo_size, logo_size), back_color)
                logo_bg.paste(logo, (0, 0), logo if logo.mode == 'RGBA' else None)
                
                # Paste logo in center
                logo_pos = ((qr_width - logo_size) // 2, (qr_height - logo_size) // 2)
                img.paste(logo_bg, logo_pos)
            
            # Display QR code
            st.success("✅ QR Code Generated Successfully!")
            st.image(img, caption="Your Artistic QR Code", use_container_width=True)
            
            # Download button
            buf = io.BytesIO()
            img.save(buf, format="PNG")
            byte_im = buf.getvalue()
            
            st.download_button(
                label="⬇️ Download QR Code",
                data=byte_im,
                file_name="artistic_qrcode.png",
                mime="image/png"
            )
            
        except Exception as e:
            st.error(f"❌ Error generating QR code: {str(e)}")

# Footer
st.markdown("---")
st.markdown("""
    <div style='text-align: center; color: #666;'>
        <p>💡 <strong>Tip:</strong> Higher error correction allows for more artistic styles and logo placement!</p>
    </div>
    """, unsafe_allow_html=True)