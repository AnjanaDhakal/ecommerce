const DEVANAGARI_SAMPLE = 'खाजा घर'

export const PRINT_FONT_FAMILY =
  "'Montserrat', 'Noto Sans Devanagari', 'Nirmala UI', 'Mangal', 'Kohinoor Devanagari', sans-serif"

export const waitForPrintFonts = async () => {
  if (typeof document === 'undefined' || !document.fonts?.load) return

  try {
    await Promise.all([
      document.fonts.load(
        '400 16px "Noto Sans Devanagari"',
        DEVANAGARI_SAMPLE,
      ),
      document.fonts.load(
        '700 16px "Noto Sans Devanagari"',
        DEVANAGARI_SAMPLE,
      ),
    ])
    await document.fonts.ready
  } catch (error) {
    // The system-font fallbacks in PRINT_FONT_FAMILY still allow printing.
    console.warn('Could not preload the Devanagari print font.', error)
  }
}
