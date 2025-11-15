const { SlashCommandBuilder } = require('discord.js');

module.exports = {
    data: new SlashCommandBuilder()
        .setName('queue')
        .setDescription('Show the current music queue'),
    async execute(interaction) {
        await interaction.reply({
            content: '📜 Müzik özelliği henüz geliştirilme aşamasındadır.',
            ephemeral: true
        });
    }
};
