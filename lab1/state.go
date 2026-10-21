package main

import (
	"image/color"

	"fyne.io/fyne/v2/canvas"
	"fyne.io/fyne/v2/widget"
)

type AppState struct {
	isUpdating         bool
	slR, slG, slB      *widget.Slider
	slC, slM, slY, slK *widget.Slider
	slH, slL, slS      *widget.Slider
	enR, enG, enB      *FocusEntry
	enC, enM, enY, enK *FocusEntry
	enH, enL, enS      *FocusEntry
	colorRect          *canvas.Rectangle
	enHex              *FocusEntry
	palette            *CustomPalette
}

func (app *AppState) setCMYK(cmyk CMYK) {
	app.slC.SetValue(float64(cmyk.C))
	app.slM.SetValue(float64(cmyk.M))
	app.slY.SetValue(float64(cmyk.Y))
	app.slK.SetValue(float64(cmyk.K))
}

func (app *AppState) setHLS(hls HLS) {
	app.slH.SetValue(float64(hls.H))
	app.slL.SetValue(float64(hls.L))
	app.slS.SetValue(float64(hls.S))
}

func (app *AppState) setRGB(rgb RGB) {
	app.slR.SetValue(float64(rgb.R))
	app.slG.SetValue(float64(rgb.G))
	app.slB.SetValue(float64(rgb.B))
}

func (app *AppState) getRGB() RGB {
	return RGB{
		R: uint8(app.slR.Value),
		G: uint8(app.slG.Value),
		B: uint8(app.slB.Value),
	}
}

func (app *AppState) getCMYK() CMYK {
	return CMYK{
		C: uint8(app.slC.Value),
		M: uint8(app.slM.Value),
		Y: uint8(app.slY.Value),
		K: uint8(app.slK.Value),
	}
}

func (app *AppState) getHLS() HLS {
	return HLS{
		H: uint16(app.slH.Value),
		L: uint8(app.slL.Value),
		S: uint8(app.slS.Value),
	}
}

func (app *AppState) updateFromRGB() {
	app.isUpdating = true
	defer func() { app.isUpdating = false }()

	rgb := app.getRGB()
	cmyk := rgb.ToCMYK()
	hls := rgb.ToHLS()

	app.setCMYK(cmyk)
	app.setHLS(hls)
	app.palette.SetColor(hls)

	app.updateLeftPanel(rgb)
}

func (app *AppState) updateFromCMYK() {
	app.isUpdating = true
	defer func() { app.isUpdating = false }()

	cmyk := app.getCMYK()
	rgb := cmyk.ToRGB()
	hls := rgb.ToHLS()

	app.setRGB(rgb)
	app.setHLS(hls)
	app.palette.SetColor(hls)

	app.updateLeftPanel(rgb)
}

func (app *AppState) updateFromHLS() {
	app.isUpdating = true
	defer func() { app.isUpdating = false }()

	hls := app.getHLS()
	rgb := hls.ToRGB()
	cmyk := rgb.ToCMYK()

	app.setRGB(rgb)
	app.setCMYK(cmyk)
	app.palette.SetColor(hls)

	app.updateLeftPanel(rgb)
}

func (app *AppState) updateLeftPanel(rgb RGB) {
	app.colorRect.FillColor = color.RGBA{R: rgb.R, G: rgb.G, B: rgb.B, A: 255}
	app.colorRect.Refresh()
	app.enHex.SetText(rgb.ToHEX())
}

func (app *AppState) updateFromHEX(hexStr string) {
	rgb, err := HEXToRGB(hexStr)
	if err != nil {
		return
	}

	app.isUpdating = true
	defer func() { app.isUpdating = false }()

	cmyk := rgb.ToCMYK()
	hls := rgb.ToHLS()

	app.setRGB(rgb)
	app.setCMYK(cmyk)
	app.setHLS(hls)
	app.palette.SetColor(hls)

	app.colorRect.FillColor = color.RGBA{R: rgb.R, G: rgb.G, B: rgb.B, A: 255}
	app.colorRect.Refresh()
}
