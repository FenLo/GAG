const { SlashCommandBuilder } = require('discord.js');

module.exports = {
    data: new SlashCommandBuilder()
        .setName('skip')
        .setDescription('Skip the currently playing song'),
    async execute(interaction) {
        await interaction.reply({
            content: '⏭️ Müzik özelliği henüz geliştirilme aşamasındadır.',
            ephemeral: true
        });
    }
};
