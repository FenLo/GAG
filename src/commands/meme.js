const { SlashCommandBuilder } = require('discord.js');
const axios = require('axios');

module.exports = {
    data: new SlashCommandBuilder()
        .setName('meme')
        .setDescription('Rastgele bir meme gönderir.'),
    async execute(interaction) {
        await interaction.deferReply();

        try {
            const response = await axios.get('https://meme-api.com/gimme');
            const meme = response.data;
            
            await interaction.followUp({
                content: `**${meme.title}**\n${meme.url}`,
            });
        } catch (error) {
            console.error('Meme error:', error);
            await interaction.followUp({ content: '❌ Meme alınamadı.', ephemeral: true });
        }
    }
};
