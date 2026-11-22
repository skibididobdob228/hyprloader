import QtQuick

Canvas {
    id: art
    required property color background
    onBackgroundChanged: requestPaint()
    onWidthChanged: requestPaint()
    onHeightChanged: requestPaint()

    onPaint: {
        const ctx = getContext("2d")
        ctx.reset()
        const w = width
        const h = height
        const compact = Math.max(0, Math.min(1, (940 - w) / 410))
        const span = Math.min(w * (0.59 - 0.18 * compact), h * 0.99)
        const offset = w * 0.14 * compact

        function gradient(x1, y1, x2, y2, stops) {
            const fill = ctx.createLinearGradient(x1 * span - offset, y1 * h,
                                                  x2 * span - offset, y2 * h)
            for (const stop of stops)
                fill.addColorStop(stop[0], stop[1])
            return fill
        }

        function facet(points, fill) {
            ctx.beginPath()
            ctx.moveTo(points[0][0] * span - offset, points[0][1] * h)
            for (let i = 1; i < points.length; ++i)
                ctx.lineTo(points[i][0] * span - offset, points[i][1] * h)
            ctx.closePath()
            ctx.fillStyle = fill
            ctx.fill()
        }

        const charcoal = ctx.createLinearGradient(0, 0, w * 0.9, h)
        charcoal.addColorStop(0, Qt.lighter(background, 1.18))
        charcoal.addColorStop(0.56, background)
        charcoal.addColorStop(1, Qt.darker(background, 1.25))
        ctx.fillStyle = charcoal
        ctx.fillRect(0, 0, w, h)

        facet([[-0.2, 0.66], [0.50, 0.34], [0.07, 1.015], [-0.2, 1.05]],
              gradient(0.05, 0.64, 0.48, 0.70, [[0, "#071b23"], [1, "#1d272b"]]))
        facet([[-0.2, 0.59], [0.47, 0.31], [-0.01, 1.035], [-0.2, 1.04]],
              gradient(0.11, 0.74, 0.38, 0.40, [[0, "#10c3d7"], [0.56, "#0aadc5"], [1, "#09647a"]]))
        facet([[-0.08, 0.52], [0.36, 0.36], [-0.02, 0.85]],
              gradient(0.03, 0.67, 0.25, 0.62, [[0, "#19dbea"], [0.48, "#04a8c0"], [1, "#04616f"]]))
        facet([[0, 0.85], [0.36, 0.36], [0.45, 0.34], [0.01, 0.99]],
              gradient(0.06, 0.77, 0.15, 0.80, [[0, "rgba(3, 99, 123, 0.4)"], [1, "rgba(19, 196, 212, 0)"]]))

        facet([[-0.15, 0.73], [1.04, -0.10], [1.19, -0.10], [-0.15, 0.83]],
              gradient(0.48, 0.29, 0.54, 0.37, [[0, "#080d13"], [1, "rgba(16, 21, 29, 0)"]]))
        facet([[-0.15, 0.69], [1.015, -0.12], [1.16, -0.12], [-0.15, 0.785]],
              gradient(0.46, 0.245, 0.54, 0.36, [[0, "#70838e"], [0.38, "#c6d4db"], [0.75, "#8fa8b3"], [1, "#516771"]]))
        facet([[-0.15, 0.66], [0.974, -0.12], [1.015, -0.12], [-0.15, 0.69]],
              gradient(0.28, 0.345, 0.31, 0.39, [[0, "#14181f"], [1, "#070b10"]]))
        facet([[-0.15, 0.648], [0.958, -0.12], [0.974, -0.12], [-0.15, 0.66]],
              gradient(0, 0.51, 0.85, 0, [[0, "#71929f"], [0.44, "#e3f4fa"], [1, "#f6fdff"]]))
    }
}
