import bpy
import os
import tempfile
import requests

bl_info = {
    "name": "Render Completed Telegram Notifier 2.0",
    "author": "Klimasevskiy",
    "version": (1, 0),
    "blender": (3, 3, 0),
    "location": "Render Properties > Render Engine",
    "description": "Sends a Telegram notification when a render is complete",
    "doc_url": "https://github.com/klimasevskiy/Render-Completed-Telegram-Notifier",
    "tracker_url": "https://t.me/klimasevskiy",
    "category": "Render"
}



def telegram_send_message(context, message, send_image):
    if not bpy.context.preferences.addons[__name__].preferences.active:
        return 
    
    bot_token = bpy.context.preferences.addons[__name__].preferences.bot_token
    chat_id = bpy.context.preferences.addons[__name__].preferences.chat_id
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"


    data = {
        "chat_id": chat_id,
        "text": message
    }
    response = requests.post(url, json=data)
    print("Message sent")
    if response.status_code != 200:
        print("Could not send message to Telegram. Please check your preferences")

    if send_image:        
        # Save rendered image to temporary file
        img_path = os.path.join(tempfile.gettempdir(), "render.png")
        bpy.data.images["Render Result"].save_render(img_path)

        # Upload image to Telegram
        url = f"https://api.telegram.org/bot{bot_token}/sendPhoto"
        data = {
            "chat_id": chat_id,
            "caption": "Rendered image",
        }
        files = {
            "photo": open(img_path, "rb"),
        }
        response = requests.post(url, data=data, files=files)
        if response.status_code != 200:
           print("Could not send rendered image to Telegram. Please check your preferences")



def start_sequence(context):
    C = bpy.context
    filepath = bpy.path.basename(C.blend_data.filepath) or '<noname>'
    start = C.scene.frame_start
    end = C.scene.frame_end
    total = end - start + 1
    message = f"_________\nStart render {filepath}\n({total} frames, {start}-{end}):"
    telegram_send_message(context, message)

def render(context):
    C = bpy.context
    curr = bpy.context.scene.frame_current
    send_image = bpy.context.preferences.addons[__name__].preferences.send_image
    telegram_send_message(context, f"Frame {curr} finished", send_image)

def render_cancel(context):
    telegram_send_message(context, "Render cancelled!")
      


class RenderCompletePanel(bpy.types.AddonPreferences):
    bl_idname = __name__

    # 7914278472:AAHbW8ndOYwdlThfwZU_WhhhGVA_2Sag8wk
    # 127847568

    bot_token: bpy.props.StringProperty(name="Bot token", description="Bot token")
    chat_id: bpy.props.StringProperty(name="Chat ID", description="Chat ID")
    active: bpy.props.BoolProperty(name="Active", description="Active")
    send_image: bpy.props.BoolProperty(name="Send image", description="Send image")
    
    def draw(self, context):
        layout = self.layout
        layout.prop(self, "bot_token")
        layout.prop(self, "chat_id")
        layout.prop(self, "active")
        if self.active:
            layout.prop(self, "send_image")

def register():
    bpy.utils.register_class(RenderCompletePanel)

    bpy.app.handlers.render_init.append(start_sequence)
    bpy.app.handlers.render_post.append(render)
    bpy.app.handlers.render_cancel.append(render_cancel)
    #bpy.app.handlers.render_complete.append(complete_sequence)
    #bpy.app.handlers.render_write.append(write)
    #bpy.app.handlers.render_stats.append(stats)
    
    bpy.app.handlers.persistent(start_sequence)
    bpy.app.handlers.persistent(render)
    bpy.app.handlers.persistent(render_cancel)
    #bpy.app.handlers.persistent(complete_sequence)
    #bpy.app.handlers.persistent(write)
    #bpy.app.handlers.persistent(stats)


def unregister():
    bpy.app.handlers.render_init.remove(start_sequence)
    bpy.app.handlers.render_post.remove(render)
    bpy.app.handlers.render_cancel.remove(render_cancel)
    #bpy.app.handlers.render_complete.remove(complete_sequence)
    #bpy.app.handlers.render_write.remove(write)
    #bpy.app.handlers.render_stats.remove(stats)
        
    bpy.utils.unregister_class(RenderCompletePanel)


if __name__ == "__main__":
    register()