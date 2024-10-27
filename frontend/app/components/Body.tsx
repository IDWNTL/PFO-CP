'use client'

import './Body.css';
import { useEffect, useRef, useState } from "react";
import axios from 'axios';

interface Message {
    text?: string;
    type: 'bot' | 'user';
    imageUrl?: string;
    centered?: boolean;
    error?: boolean;
}

const Body = () => {
    const [messages, setMessages] = useState<Message[]>([
        { text: 'Добрый день, могу ли я вам помочь?', type: 'bot', imageUrl: '/Logo.png', centered: true },
    ]);

    const [inputValue, setInputValue] = useState('');
    const [selectedFile, setSelectedFile] = useState<File | null>(null);
    const [modalImageUrl, setModalImageUrl] = useState<string | null>(null);

    const textAreaRef = useRef<HTMLTextAreaElement>(null);
    const buttonContainerRef = useRef<HTMLDivElement>(null);
    const fileInputRef = useRef<HTMLInputElement>(null);

    // Добавляем массив часто задаваемых вопросов
    const frequentlyAskedQuestions = [
        'Что такое «Шаблон»?',
        'Как создать требование?',
        'Закончилась лицензия КК – как продлить?',
        'Можно ли создать копию профиля?'
    ];

    useEffect(() => {
        if (textAreaRef.current) {
            textAreaRef.current.style.height = 'auto';
            textAreaRef.current.style.height = Math.min(textAreaRef.current.scrollHeight, 150) + 'px';
        }
        if (buttonContainerRef.current) {
            buttonContainerRef.current.style.height = textAreaRef.current ? textAreaRef.current.style.height : '40px';
        }
    }, [inputValue]);

    useEffect(() => {
        if (textAreaRef.current && buttonContainerRef.current) {
            buttonContainerRef.current.style.height = textAreaRef.current.style.height;
        }
    }, [messages]);

    const handleSendMessage = async () => {
        if (inputValue.trim() || selectedFile) {
            const newMessage: Message = { type: 'user' };
            if (inputValue.trim()) {
                newMessage.text = inputValue.trim();
            }
            if (selectedFile) {
                const fileUrl = URL.createObjectURL(selectedFile);
                newMessage.imageUrl = fileUrl;
            }
            setMessages((prevMessages) => [...prevMessages, newMessage]);

            try {
                const formData = new FormData();
                if (inputValue.trim()) {
                    formData.append('text', inputValue.trim());
                }
                if (selectedFile) {
                    formData.append('image', selectedFile, selectedFile.name);
                }

                await axios.post('/api/sendMessage', formData, {
                    headers: {
                        'Content-Type': 'multipart/form-data'
                    }
                });
            } catch (error) {
                console.error('Ошибка при отправке сообщения:', error);
                setMessages((prevMessages) => {
                    const updatedMessages = [...prevMessages];
                    updatedMessages[updatedMessages.length - 1].error = true;
                    return updatedMessages;
                });
            }

            setInputValue('');
            setSelectedFile(null);
            if (fileInputRef.current) {
                fileInputRef.current.value = '';
            }
            if (textAreaRef.current && buttonContainerRef.current) {
                textAreaRef.current.style.height = '40px';
                buttonContainerRef.current.style.height = '40px';
            }
        }
    };

    const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const file = e.target.files ? e.target.files[0] : null;
        if (file) {
            setSelectedFile(file);
        }
    };

    const handleSpeechToText = () => {
        if ('webkitSpeechRecognition' in window) {
            const recognition = new (window as any).webkitSpeechRecognition();
            recognition.lang = 'ru-RU';
            recognition.interimResults = false;
            recognition.maxAlternatives = 1;

            recognition.onresult = (event: any) => {
                const transcript = event.results[0][0].transcript;
                setInputValue(transcript);
            };

            recognition.onerror = (event: any) => {
                console.error('Ошибка распознавания речи:', event.error);
            };

            recognition.start();
        } else {
            alert('Ваш браузер не поддерживает распознавание речи');
        }
    };

    const openImageModal = (imageUrl: string) => {
        setModalImageUrl(imageUrl);
    };

    const closeImageModal = () => {
        setModalImageUrl(null);
    };

    return (
        <div className="flex flex-col h-screen bg-background w-full md:w-1/2">
            <div className="flex-grow p-4 overflow-y-auto z-0 custom-scrollbar"
                 style={{flex: '1 1 auto', maxHeight: 'calc(100vh - 160px)', minHeight: 'calc(100vh - 160px)'}}>
                {messages.map((message, index) => (
                    <div
                        key={index}
                        className={`mb-2 p-4 rounded-lg break-words w-fit max-w-full ${
                            message.type === 'user' ? 'bg-colorForMain text-white self-end' : message.centered ? 'bg-purple-300 text-black mx-auto' : 'bg-purple-300 text-black self-start'
                        }`}
                    >
                        {message.type === 'bot' && message.imageUrl && (
                            <div className="flex justify-center mb-2">
                                <img src={message.imageUrl} alt="Bot logo" className="max-w-xs max-h-32 object-contain mx-auto" onClick={() => openImageModal(message.imageUrl!)} />
                            </div>
                        )}
                        {message.text && (
                            <div className={`whitespace-pre-wrap break-words w-full ${message.type === 'bot' ? 'text-center' : ''}`}>
                                {message.text}
                            </div>
                        )}
                        {message.type === 'user' && message.imageUrl && (
                            <img src={message.imageUrl} alt="Uploaded file" className="max-w-full h-auto mt-2 rounded-lg object-contain" onClick={() => openImageModal(message.imageUrl!)} />
                        )}
                        {message.error && (
                            <div className="text-red-500 mt-2">Ошибка отправки</div>
                        )}
                    </div>
                ))}
            </div>
            <div className="p-4 bg-background shadow-md">
                {/* Добавляем теги часто задаваемых вопросов */}
                <div className="flex overflow-x-auto mb-2 space-x-2 custom-scrollbar-bottom">
                    {frequentlyAskedQuestions.map((question, index) => (
                        <button
                            key={index}
                            onClick={() => setInputValue(question)}
                            className="flex-shrink-0 px-3 py-1 bg-colorForMain text-white rounded-full hover:bg-white hover:text-black focus:outline-none focus:ring-2 focus:ring-blue-500 whitespace-nowrap"
                        >
                            {question}
                        </button>
                    ))}
                </div>
                <div className="flex items-center" ref={buttonContainerRef}>
                    <textarea
                        ref={textAreaRef}
                        value={inputValue}
                        onChange={(e) => setInputValue(e.target.value)}
                        onKeyDown={(e) => e.key === 'Enter' && !e.shiftKey && (e.preventDefault(), handleSendMessage())}
                        className="flex-grow p-2 border border-gray-300 rounded-l-lg focus:outline-none focus:ring-2 focus:ring-colorForMain text-black resize-none overflow-y-auto custom-scrollbar"
                        placeholder="Введите сообщение..."
                        rows={1}
                    />
                    <input
                        type="file"
                        onChange={handleFileChange}
                        className="hidden"
                        id="fileInput"
                        accept="image/*"
                        ref={fileInputRef}
                    />
                    <label
                        htmlFor="fileInput"
                        className="cursor-pointer p-2 border border-gray-300 bg-colorForMain hover:bg-gray-300 h-auto flex items-center"
                        style={{height: textAreaRef.current ? textAreaRef.current.style.height : '40px'}}
                    >
                        <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24"
                             stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                                  d="M12 6v6m0 0v6m0-6h6m-6 0H6"/>
                        </svg>
                    </label>
                    <button
                        onClick={handleSendMessage}
                        className="ml-2 p-2 bg-colorForMain text-white rounded-lg hover:bg-white hover:text-black focus:outline-none focus:ring-2 focus:ring-blue-500 h-auto flex items-center"
                        style={{height: textAreaRef.current ? textAreaRef.current.style.height : '40px'}}>
                        Отправить
                    </button>
                    <button
                        onClick={handleSpeechToText}
                        className="ml-2 p-2 bg-colorForMain text-white rounded-lg hover:bg-white hover:text-black focus:outline-none focus:ring-2 focus:ring-blue-500 h-auto flex items-center"
                        style={{height: textAreaRef.current ? textAreaRef.current.style.height : '40px'}}>
                        🎙️
                    </button>
                </div>
                {selectedFile && (
                    <div className="mt-2">
                        <p>Выбран файл: {selectedFile.name}</p>
                    </div>
                )}
            </div>

            {modalImageUrl && (
                <div className="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-50" onClick={closeImageModal}>
                    <img src={modalImageUrl} alt="Modal" className="max-w-full max-h-full object-contain" />
                </div>
            )}
        </div>
    );
};

export default Body;
