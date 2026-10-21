package main

import (
	"fmt"
	"image/color"
	"strconv"

	"fyne.io/fyne/v2"
	"fyne.io/fyne/v2/canvas"
	"fyne.io/fyne/v2/container"
	"fyne.io/fyne/v2/widget"
)

type FocusEntry struct {
	widget.Entry
	OnFocusLost func()
}

func NewFocusEntry() *FocusEntry {
	e := &FocusEntry{}
	e.ExtendBaseWidget(e)
	return e
}

func (e *FocusEntry) FocusLost() {
	e.Entry.FocusLost()
	if e.OnFocusLost != nil {
		e.OnFocusLost()
	}
}

func (app *AppState) createChannel(name string, mn, mx float64, onChange func()) (*widget.Slider, *FocusEntry, *fyne.Container) {
	slider := widget.NewSlider(mn, mx)
	slider.Step = 1
	entry := NewFocusEntry()
	entry.SetText(fmt.Sprintf("%.0f", mn))
	label := widget.NewLabel(name)
	slider.OnChanged = func(val float64) {
		entry.SetText(fmt.Sprintf("%.0f", val))
		if !app.isUpdating {
			onChange()
		}
	}
	entry.OnFocusLost = func() {
		val, err := strconv.ParseFloat(entry.Text, 64)
		if err != nil || val < mn || val > mx {
			entry.SetText(fmt.Sprintf("%.0f", slider.Value))
		}
	}
	entry.OnSubmitted = func(text string) {
		entry.OnFocusLost()
	}
	entry.OnChanged = func(text string) {
		val, err := strconv.ParseFloat(text, 64)
		if err == nil && val >= mn && val <= mx {
			slider.SetValue(val)
		}
	}
	entrySize := container.NewGridWrap(fyne.NewSize(50, 37), entry)
	row := container.NewBorder(nil, nil, label, entrySize, slider)
	return slider, entry, row
}

func (app *AppState) buildRightPanel() *fyne.Container {
	var rowR, rowG, rowB *fyne.Container
	app.slR, app.enR, rowR = app.createChannel("R (Red):", 0, 255, app.updateFromRGB)
	app.slG, app.enG, rowG = app.createChannel("G (Green):", 0, 255, app.updateFromRGB)
	app.slB, app.enB, rowB = app.createChannel("B (Blue):", 0, 255, app.updateFromRGB)

	rgbCard := widget.NewCard("Модель RGB", "Аддитивная модель", container.NewVBox(rowR, rowG, rowB))

	var rowC, rowM, rowY, rowK *fyne.Container
	app.slC, app.enC, rowC = app.createChannel("C (Cyan):", 0, 100, app.updateFromCMYK)
	app.slM, app.enM, rowM = app.createChannel("M (Magenta):", 0, 100, app.updateFromCMYK)
	app.slY, app.enY, rowY = app.createChannel("Y (Yellow):", 0, 100, app.updateFromCMYK)
	app.slK, app.enK, rowK = app.createChannel("K (Key/Black):", 0, 100, app.updateFromCMYK)

	cmykCard := widget.NewCard("Модель CMYK", "Субтрактивная модель", container.NewVBox(rowC, rowM, rowY, rowK))

	var rowH, rowL, rowS *fyne.Container
	app.slH, app.enH, rowH = app.createChannel("H (Hue):", 0, 360, app.updateFromHLS)
	app.slL, app.enL, rowL = app.createChannel("L (Lightness):", 0, 100, app.updateFromHLS)
	app.slS, app.enS, rowS = app.createChannel("S (Saturation):", 0, 100, app.updateFromHLS)

	hlsCard := widget.NewCard("Модель HLS", "Перцепционная модель", container.NewVBox(rowH, rowL, rowS))

	return container.NewVBox(rgbCard, cmykCard, hlsCard)
}

func (app *AppState) buildLeftPanel() *fyne.Container {
	app.colorRect = canvas.NewRectangle(color.RGBA{A: 255})
	app.colorRect.SetMinSize(fyne.NewSize(100, 80))

	app.enHex = NewFocusEntry()
	app.enHex.SetText("#000000")
	app.enHex.OnChanged = func(s string) {
		if !app.isUpdating {
			app.updateFromHEX(s)
		}
	}
	app.enHex.OnFocusLost = func() {
		_, err := HEXToRGB(app.enHex.Text)
		if err != nil {
			app.enHex.SetText(app.getRGB().ToHEX())
		}
	}
	app.enHex.OnSubmitted = func(text string) {
		app.enHex.OnFocusLost()
	}
	hexRow := container.NewBorder(nil, nil, widget.NewLabel("HEX:"), nil, app.enHex)

	app.palette = NewCustomPalette(func(hls HLS) {
		if !app.isUpdating {
			app.setHLS(hls)
			app.updateFromHLS()
		}
	})

	bottomBox := container.NewVBox(hexRow, app.colorRect)

	return container.NewBorder(nil, bottomBox, nil, nil, app.palette.Container)
}
