# Gamma 校正（提升暗部细节）
def gamma_correction(y_channel, gamma=1.5):
    result = [[
        round((pix / 255) ** gamma * 255)
        for pix in row
    ] for row in y_channel]
    return result