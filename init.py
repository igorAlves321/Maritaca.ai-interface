# -*- coding: utf-8 -*- 
import wx
import maritalk
import json
import os

with open('apiKey.txt', 'r') as file:
    apiKey = file.read().strip()

model = maritalk.MariTalk(key=apiKey)

if os.path.exists('conversations.json'):
    with open('conversations.json', 'r') as file:
        messages = json.load(file)
else:
    messages = []

class ChatInterface(wx.Frame):
    def __init__(self, *args, **kwargs):
        super(ChatInterface, self).__init__(*args, **kwargs)

        self.InitUI()
        self.Bind(wx.EVT_CHAR_HOOK, self.on_key_down)

    def InitUI(self):
        panel = wx.Panel(self)
        vbox = wx.BoxSizer(wx.VERTICAL)

        # Lista de Mensagens
        self.messages_list = wx.ListBox(panel, style=wx.LB_SINGLE)
        self.messages_list.SetName('Lista de Mensagens')
        for message in messages:
            if message['role'] == 'user':
                self.messages_list.Append('User: ' + message['content'])
            else:
                self.messages_list.Append('Assistant: ' + message['content'])
        self.messages_list.Bind(wx.EVT_LISTBOX, self.on_list_select)
        vbox.Add(self.messages_list, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=10)

        # Mensagem Selecionada
        self.selected_message = wx.TextCtrl(panel, style=wx.TE_READONLY|wx.TE_MULTILINE)
        self.selected_message.SetName('Mensagem Selecionada')
        vbox.Add(self.selected_message, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=10)

        hbox2 = wx.BoxSizer(wx.HORIZONTAL)

        # Campo para Nova Mensagem
        self.new_message = wx.TextCtrl(panel, style=wx.TE_MULTILINE)
        self.new_message.SetName('Campo para Nova Mensagem')
        hbox2.Add(self.new_message, proportion=1)

        # Botão Enviar
        send_button = wx.Button(panel, label='&Enviar')
        send_button.SetName('Botão Enviar')
        send_button.Bind(wx.EVT_BUTTON, self.send_message)
        hbox2.Add(send_button, flag=wx.LEFT, border=5)
        # Botão Limpar

        clear_button = wx.Button(panel, label='&Limpar', name='Limpar o chat')
        clear_button.Bind(wx.EVT_BUTTON, self.on_clear)
        hbox2.Add(clear_button, flag=wx.LEFT, border=5)

        # Botão Cancelar
        cancel_button = wx.Button(panel, label='&Cancelar')
        cancel_button.SetName('Botão Cancelar')
        cancel_button.Bind(wx.EVT_BUTTON, self.on_cancel)
        hbox2.Add(cancel_button, flag=wx.LEFT, border=5)

        vbox.Add(hbox2, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=10)

        panel.SetSizer(vbox)

    def on_key_down(self, event):
        if event.GetKeyCode() == wx.WXK_ESCAPE:
            self.Close()
        else:
            event.Skip()

    def on_list_select(self, event):
        self.selected_message.SetValue(self.messages_list.GetString(self.messages_list.GetSelection()))

    def on_clear(self, event):
        self.messages_list.Clear()
        self.selected_message.Clear()
        self.new_message.Clear()
        global messages
        messages = []

    def send_message(self, event):
        user_message = self.new_message.GetValue()
        messages.append({"role": "user", "content": user_message})
        assistant_message = model.generate(
            messages,
            do_sample=True,
            max_tokens=200,
            temperature=0.7,
            top_p=0.95
        )
        messages.append({"role": "assistant", "content": assistant_message})
        self.messages_list.Append('User: ' + user_message)
        self.messages_list.Append('Assistant: ' + assistant_message)
        self.new_message.Clear()

        with open('conversations.json', 'w') as file:
            json.dump(messages, file)

    def on_cancel(self, event):
        self.Close()

def main():
    app = wx.App()
    ChatInterface(None, title='Chat Interface').Show()
    app.MainLoop()

if __name__ == "__main__":
    main()
