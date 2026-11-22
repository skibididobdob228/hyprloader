hl.monitor({ output = "", mode = "preferred", position = "auto", scale = 1 })

hl.config({
  animations = { enabled = false },
  misc = {
    background_color = "rgb(242527)",
    disable_hyprland_logo = true,
    disable_splash_rendering = true,
  },
  xwayland = { enabled = false },
})

hl.bind("SUPER + ESCAPE", hl.dsp.exit())

hl.on("hyprland.start", function()
  local command = os.getenv("HYPRLOADER_MENU_COMMAND")
  if command then
    hl.exec_cmd(command)
  else
    hl.dispatch(hl.dsp.exit())
  end
end)
