const { SlashCommandBuilder } = require('discord.js');

// Drawing game state
const games = new Map();

module.exports = {
    data: new SlashCommandBuilder()
        .setName('drawgame')
        .setDescription('Bir çizim oyunu başlatır. (Kelime DM ile gönderilir)'),
    async execute(interaction) {
        await interaction.reply({
            content: '🎨 Çizim oyunu özelliği henüz geliştirilme aşamasındadır. Yakında aktif olacak!',
            ephemeral: true
        });
        
        // TODO: Implement drawing game
        // Features:
        // - Random word selection
        // - Send word via DM
        // - Track guesses
        // - Award points
    }
};
