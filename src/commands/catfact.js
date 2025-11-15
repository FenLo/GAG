const { SlashCommandBuilder } = require('discord.js');
const axios = require('axios');

module.exports = {
    data: new SlashCommandBuilder()
        .setName('catfact')
        .setDescription('Rastgele bir kedi gerçeği gönderir.'),
    async execute(interaction) {
        await interaction.deferReply();

        try {
            const response = await axios.get('https://catfact.ninja/fact');
            const fact = response.data.fact;
            await interaction.followUp(`🐱 **Kedi Gerçeği:** ${fact}`);
        } catch (error) {
            console.error('Cat fact error:', error);
            await interaction.followUp({ content: '❌ Kedi gerçeği alınamadı.', ephemeral: true });
        }
    }
};
