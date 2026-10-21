package main

import (
	"fyne.io/fyne/v2"
	"fyne.io/fyne/v2/app"
	"fyne.io/fyne/v2/container"
)

func main() {
	a := app.New()
	w := a.NewWindow("Lab1 (CMYK, RGB, HLS) by Pavel Ryzhou")
	appState := &AppState{}
	leftPanel := appState.buildLeftPanel()
	rightPanel := appState.buildRightPanel()
	split := container.NewHSplit(leftPanel, rightPanel)
	split.Offset = 0.4
	w.SetContent(split)
	w.Resize(fyne.NewSize(800, 600))
	appState.updateFromRGB()
	w.ShowAndRun()
}
