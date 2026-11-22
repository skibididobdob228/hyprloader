import QtQuick

Canvas {
    id: icon
    required property string kind
    required property color ink
    onKindChanged: requestPaint()
    onInkChanged: requestPaint()
    onWidthChanged: requestPaint()
    onHeightChanged: requestPaint()

    onPaint: {
        const ctx = getContext("2d")
        ctx.reset()
        ctx.clearRect(0, 0, width, height)
        ctx.scale(width / 24, height / 24)
        ctx.strokeStyle = ink
        ctx.fillStyle = ink
        ctx.lineWidth = 1.65
        ctx.lineJoin = "round"
        ctx.lineCap = "round"

        function line(points, closed = false) {
            ctx.beginPath()
            ctx.moveTo(points[0][0], points[0][1])
            for (let i = 1; i < points.length; ++i)
                ctx.lineTo(points[i][0], points[i][1])
            if (closed)
                ctx.closePath()
            ctx.stroke()
        }

        switch (kind) {
        case "default":
            ctx.strokeRect(3, 4, 18, 13)
            line([[12, 17], [12, 21]])
            line([[8, 21], [16, 21]])
            break
        case "minimal":
            ctx.strokeRect(4, 5, 16, 14)
            line([[4, 9], [20, 9]])
            line([[8, 15], [14, 15]])
            break
        case "cosmos":
            ctx.beginPath()
            ctx.arc(12, 12, 5.3, 0, 2 * Math.PI)
            ctx.stroke()
            ctx.save()
            ctx.translate(12, 12)
            ctx.rotate(-Math.PI / 5)
            ctx.scale(1, 0.32)
            ctx.beginPath()
            ctx.arc(0, 0, 10, 0, 2 * Math.PI)
            ctx.stroke()
            ctx.restore()
            break
        case "backrooms":
            line([[4, 21], [4, 4], [20, 4], [20, 21]])
            line([[8, 21], [8, 8], [16, 8], [16, 21]])
            line([[6, 21], [18, 21]])
            break
        case "superlab":
            line([[8, 3], [16, 3]])
            line([[10, 3], [10, 10], [4, 19], [5, 21], [19, 21], [20, 19], [14, 10], [14, 3]])
            line([[8, 15], [16, 15]])
            break
        default:
            line([[12, 3], [21, 8], [12, 13], [3, 8]], true)
            line([[3, 12], [12, 17], [21, 12]])
            line([[3, 16], [12, 21], [21, 16]])
        }
    }
}
